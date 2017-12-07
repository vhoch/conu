import logging
import os
import shutil
from tempfile import mkdtemp

from conu.exceptions import ConuException

logger = logging.getLogger(__name__)


class Filesystem(object):
    """
    Utility methods used to access filesystem of containers and images.

    Implementations should probably be done using context managers.
    """
    def __init__(self, object_instance, mount_point=None):
        """
        :param object_instance: instance of the container or image
        :param mount_point: str, directory where the filesystem will be mounted
        """
        self.obj = object_instance
        self._mount_point = mount_point
        self.mount_point_provided = False

    @property
    def mount_point(self):
        if self._mount_point is None:
            self._mount_point = mkdtemp(prefix="conu")
            self.mount_point_provided = True
        return self._mount_point

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mount_point_provided:
            os.rmdir(self.mount_point)

    def p(self, path):
        """
        provide absolute path within the container

        :param path: path with container
        :return: str
        """
        if path.startswith("/"):
            path = path[1:]
        p = os.path.join(self.mount_point, path)
        logger.debug("path = %s", p)
        return p

    def copy_to(self, src, dest):
        """
        copy a file or a directory from host system to a container -- don't implement for images,
        those are immutable

        :param src: str, path to a file or a directory on host system
        :param dest: str, path to a file or a directory within container
        :return: None
        """
        raise NotImplementedError("copy_to method is not implemented")

    def copy_from(self, src, dest):
        """
        copy a file or a directory from container or image to host system. If you are copying
        directories, the target directory must not exist (this function is using `shutil.copytree`
        to copy directories and that's a requirement of the function). In case the directory exists,
        OSError on python 2 or FileExistsError on python 3 are raised.

        :param src: str, path to a file or a directory within container or image
        :param dest: str, path to a file or a directory on host system
        :return: None
        """
        p = self.p(src)
        if os.path.isfile(p):
            logger.info("copying file %s to %s", p, dest)
            shutil.copy2(p, dest)
        else:
            logger.info("copying directory %s to %s", p, dest)
            shutil.copytree(p, dest)

    def read_file(self, file_path):
        """
        read file specified via 'file_path' and return its content - raises an ConuException if
        there is an issue accessing the file

        :param file_path: str, path to the file to read
        :return: str (not bytes), content of the file
        """
        try:
            with open(self.p(file_path)) as fd:
                return fd.read()
        except IOError as ex:
            logger.error("error while accessing file %s: %r", file_path, ex)
            raise ConuException("There was an error while accessing file %s: %r", file_path, ex)

    def get_file(self, file_path, mode="r"):
        """
        provide File object specified via 'file_path'

        :param file_path: str, path to the file
        :param mode: str, mode used when opening the file
        :return: File instance
        """
        return open(self.p(file_path), mode=mode)

    def file_is_present(self, file_path):
        """
        check if file 'file_path' is present, raises IOError if file_path
        is not a file

        :param file_path: str, path to the file
        :return: True if file exists, False if file does not exist
        """
        p = self.p(file_path)
        if not os.path.exists(p):
            return False
        if not os.path.isfile(p):
            raise IOError("%s is not a file" % file_path)
        return True

    def directory_is_present(self, directory_path):
        """
        check if directory 'directory_path' is present, raise IOError if it's not a directory

        :param directory_path: str, directory to check
        :return: True if directory exists, False if directory does not exist
        """
        p = self.p(directory_path)
        if not os.path.exists(p):
            return False
        if not os.path.isdir(p):
            raise IOError("%s is not a directory" % directory_path)
        return True

    def get_selinux_context(self, file_path):
        """
        return a permissions for 'file_path'

        :param file_path: str, path to the file
        :return: str
        """
        # what if SELinux is not enabled?
        p = self.p(file_path)

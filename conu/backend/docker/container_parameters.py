from conu import DockerRunBuilder

# Parameter definitions in `docker run --help`
# Compare with https://github.com/docker/docker-py/blob/master/docker/api/container.py#L235


class ContainerParameters:
    """
    Placeholder for container parameters
    """

    def __init__(self, command=None, hostname=None, user=None,
                         detach=False, stdin_open=False, tty=False,
                         mem_limit=None, ports=None, environment=None,
                         dns=None, volumes=None, volumes_from=None,
                         network_disabled=False, name=None, entrypoint=None,
                         cpu_shares=None, working_dir=None, domainname=None,
                         memswap_limit=None, cpuset=None, host_config=None,
                         mac_address=None, labels=None, volume_driver=None,
                         stop_signal=None, networking_config=None,
                         healthcheck=None, stop_timeout=None, runtime=None):
        self.command = command
        self.hostname = hostname
        self.user = user
        self.detach = detach
        self.stdin_open = stdin_open
        self.tty = tty
        self.mem_limit = mem_limit
        self.ports = ports
        self.environment = environment
        self.dns = dns
        self.volumes = volumes
        self.volumes_from = volumes_from
        self.network_disabled = network_disabled
        self.name = name
        self.entrypoint = entrypoint
        self.cpu_shares = cpu_shares
        self.working_dir = working_dir
        self.domainname = domainname
        self.memswap_limit = memswap_limit
        self.cpuset = cpuset
        self.host_config = host_config
        self.mac_address = mac_address
        self.labels = labels
        self.volume_driver = volume_driver
        self.stop_signal = stop_signal
        self.networking_config = networking_config
        self.healthcheck = healthcheck
        self.stop_timeout = stop_timeout
        self.runtime = runtime

    @classmethod
    def create_from_drb(cls, run_builder):
        """
        Creates placeholder for container parameters from DockerRunBuilder instance

        :param run_builder: DockerRunBuilder
        :return: ContainerParamenters
        """
        table_with_parameter = {
            "e": "environment",
        }

        table_single = {
            "i": "stdin_open",
            "t": "tty",
            "d": "detach",

        }

        opts = run_builder.options
        skip = False
        options_dict = {}
        for index in range(len(opts)):
            if skip:
                skip = False
                continue
            #if opts[index][0] == "-":
            opts[index] = opts[index].strip('-')
            command = opts[index]
            try:
                option = table_with_parameter[command]
                parameter = opts[index+1]
                if option in options_dict:
                    options_dict[option].append(parameter)
                else:
                    options_dict[option] = [parameter]
                skip = True
            except KeyError:
                try:
                    option = table_single[command]
                    options_dict[option] = True
                except KeyError:
                    try:
                        for char in command:
                            option = table_single[char]
                            options_dict[option] = True
                    except KeyError:
                        pass
        conf = cls(**options_dict)

        # .......

        return conf

    def get_docker_run_builder(self):
        """
        Create DockerRunBuilder with parameters set

        :return: DockerRunBuilder
        """
        additional_opts=[]
        command = []

        # ......

        return DockerRunBuilder(additional_opts=additional_opts, command=command)




# Just for testing purposes
if __name__ == '__main__':
    drb = DockerRunBuilder(additional_opts=['-e', 'KEY=space', '-e', 'TIME=now'])
    para = ContainerParameters().create_from_drb(drb)
    assert para.environment == ["KEY=space", "TIME=now"]
    assert not para.tty

    drb = DockerRunBuilder(additional_opts=['-it'])
    para = ContainerParameters().create_from_drb(drb)
    assert para.tty
    assert para.stdin_open

    drb = DockerRunBuilder(additional_opts=['-i', '-t'])
    para = ContainerParameters().create_from_drb(drb)
    assert para.tty
    assert para.stdin_open

    #drb = DockerRunBuilder(command=['sleep', '50'])
    #para = ContainerParameters().create_from_drb(drb)
    #assert para.command == ['sleep', '50']
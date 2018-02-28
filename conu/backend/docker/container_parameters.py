from docker.types import Healthcheck

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

        import argparse
        parser = argparse.ArgumentParser(add_help=False)

        # without parameter
        parser.add_argument("-i",   "--interactive",    action="store_true", dest="stdin_open")
        parser.add_argument("-d",   "--detach",         action="store_true", dest="detach")
        parser.add_argument("-t",   "--tty",            action="store_true", dest="tty")

        # string parameter
        parser.add_argument("-h",   "--hostname",       action="store", dest="hostname")
        parser.add_argument("-u",   "--user",           action="store", dest="user")
        parser.add_argument(        "--name",           action="store", dest="name")
        parser.add_argument(        "--entrypoint",     action="store", dest="entrypoint")
        parser.add_argument("-w",   "--workdir",        action="store", dest="working_dir")
        parser.add_argument(        "--mac-address",    action="store", dest="mac_address")
        parser.add_argument(        "--stop-signal",    action="store", dest="stop_signal")
        # parser.add_argument("",                         action="store", dest="runtime")
        # parser.add_argument("",                         action="store", dest="domainname")

        # int parameter
        # parser.add_argument("",                         action="store", dest="stop_timeout", type=int)

        # list parameter
        parser.add_argument("-e",   "--env",            action="append", dest="environment")
        parser.add_argument("-p",   "--publish",        action="append", dest="ports")
        parser.add_argument(        "--volumes-from",   action="append", dest="volumes")

        # dict parameter
        parser.add_argument("-l",   "--label",          action="append", dest="labels")
        parser.add_argument(        "--net-alias",      action="append", dest="networking_config")
        # parser.add_argument("",                         action="append", dest="host_config") # return instance

        # health
        parser.add_argument(        "--health-cmd",     action="store",      dest="health_cmd")
        parser.add_argument(        "--health-interval", action="store",     dest="health_interval", type=int)
        parser.add_argument(        "--health-retries", action="store",      dest="health_retries", type=int)
        parser.add_argument(        "--health-timeout", action="store",      dest="health_timeout", type=int)
        parser.add_argument(        "--no-healthcheck", action="store_true", dest="no_healthcheck")

        # network
        # parser.add_argument(        "--network-alias",  action="append",    dest="network_alias", default=[])
        # parser.add_argument(        "--ip",             action="store",     dest="ip", default="")
        # parser.add_argument(        "--ip6",            action="store",     dest="ip6", default="")
        # parser.add_argument(        "--link-local-ip",  action="append",    dest="link_local_ip", default=[])


        args = parser.parse_args(args=run_builder.options)
        command = run_builder.arguments
        if command:
            conf = cls(command)
            return conf

        options_dict = vars(args)

        if not options_dict.pop("no_healthcheck", None):
            options_dict["healthcheck"] = Healthcheck(
                test=options_dict.pop("health_cmd", None),
                interval=options_dict.pop("health_interval", None),
                timeout=options_dict.pop("health_timeout", None),
                retries=options_dict.pop("health_retries", None)
            )
        """
        networking_config = docker_client.create_networking_config({
            'network1': docker_client.create_endpoint_config(
                ipv4_address=options_dict.pop("ip", None),
                ipv6_address=options_dict.pop("ip6", None),
                aliases=options_dict.pop("network_alias"),
                links=options_dict.pop("link_local_ip")
            )
        }) """

        with_dictionary_parameter = ['labels', 'networking_config']
        for name in with_dictionary_parameter:
            if options_dict[name] is not None:
                dictionary = {}
                for item in options_dict[name]:
                    try:
                        key, value = item.split("=")
                        dictionary[key] = value
                    except ValueError:
                        dictionary = options_dict[name]
                        break
                options_dict[name] = dictionary

        conf = cls(**options_dict)

        return conf

        # .......

    def get_docker_run_builder(self):
        """
        Create DockerRunBuilder with parameters set

        :return: DockerRunBuilder
        """
        additional_opts = []
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

    drb = DockerRunBuilder(command=['sleep', '50'])
    para = ContainerParameters().create_from_drb(drb)
    assert para.command == ['sleep', '50']

    drb = DockerRunBuilder(additional_opts=['-l', 'KEY=space'])
    para = ContainerParameters().create_from_drb(drb)
    assert para.labels == {"KEY": "space"}

    drb = DockerRunBuilder(additional_opts=['--health-interval', '47521', '--health-timeout', '15'])
    para = ContainerParameters().create_from_drb(drb)
    assert para.healthcheck['Interval'] == 47521
    assert para.healthcheck['Timeout'] == 15

    # drb = DockerRunBuilder(additional_opts=['--ip', '192.168.1.1', '--network-alias', 'hello'])
    # para = ContainerParameters().create_from_drb(drb)

import subprocess


class CmdlineUtilUnavailableException(Exception):
    pass


class CmdlineUtil:
    name: str = ""

    @classmethod
    def path(cls) -> str:
        try:
            p: subprocess.CompletedProcess = subprocess.run(
                args=["which", cls.name],
                capture_output=True,
                check=True
            )
            path = p.stdout.rstrip().decode("UTF-8")
            if not path:
                raise CmdlineUtilUnavailableException
            return path
        except subprocess.CalledProcessError as e:
            raise CmdlineUtilUnavailableException(e)
        except FileNotFoundError:
            pass

from mars import downloader


url = """\
http://mirrors.us.kernel.org/ubuntu-releases/18.04.2/ubuntu-18.04.2-live-server-amd64.iso
"""

d = downloader.Downloader(url)

d.start()

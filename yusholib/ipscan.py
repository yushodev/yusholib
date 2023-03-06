import socket

class IpRange():
  def __init__(self, start_ip, end_ip):
    start = list(map(int, start_ip.split(".")))
    end = list(map(int, end_ip.split(".")))
    temp = start
    ip_range = []

    if start[1] > 255 or start[2] > 255 or start[3] > 255 or start[4] > 255 or end[1] > 255 or end[2] > 255 or end[3] > 255 or end[4] > 255 or len(start) != 4 or len(end) != 4:
      raise ValueError("Invalid IP")

    ip_range.append(start_ip)
    while temp != end:
      start[3] += 1
      for i in (3, 2, 1):
          if temp[i] == 256:
            temp[i] = 0
            temp[i-1] += 1
      ip_range.append(".".join(map(str, temp)))

    self.ip_range = ip_range

class IpRangeScanner():
      def __init__(self, ip_range: IpRange, port: int, result_file):
        self.ip_range = ip_range.ip_range
        self.port = port
        self.result_file = result_file

      def scan(self):
        for ip in self.ip_range:
          self.__scan(ip)
      
      def __scan(self, ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
          s.connect((ip, int(self.port)))
          s.shutdown(socket.SHUT_RDWR)
          file = open(self.result_file, "a+")
          file.write(ip + "\n")
        except:
          pass
        finally:
          s.close()
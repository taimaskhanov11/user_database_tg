import re


def find_email(email):
    res = re.findall(r"(.*):(.*)", email)
    print(res)


a  = [(1, 2), (3, 4)]
x = map(lambda k: {k[0]:k[1]}, a)
print(list(x))
print(dict(a))


if __name__ == '__main__':
    pass
    # find_email("aahaantourandtravels01@gmail.com:Yog@1987")

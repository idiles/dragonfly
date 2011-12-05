from idileslib.soa import ServiceProxy

if __name__ == '__main__':
    s = ServiceProxy('http://localhost:8080/services/sample')
    r = ''
    for i in range(120):
        r += s.hello()
    print len(r)



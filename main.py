import server
import client
import sys



if __name__ == "__main__":
    print(sys.argv[0])

    numArgs = len(sys.argv)
    if numArgs != 2:
        print("incorrect number of arguments, please specify client or server with -S or -C flags")
        exit()

    if sys.argv[1] != "-S" and sys.argv[1] != "-C":
        print("incorrect second arg, please specify client or server with -S or -C flags")
    
    if sys.argv[1] == "-S":
        server.do_server()

    if sys.argv[1] == "-C":
        client.do_client()

z="global"
def outer():
    z = "local"

    def inner():
        nonlocal z
        if z == "local":
            print("Its local z only of the calling function")
    inner()
    print("outer:", z)
    print("global:",globals()["z"])

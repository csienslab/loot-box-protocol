from headstart.client import HeadStartClient

client = HeadStartClient.from_server_url("http://ws3.csie.ntu.edu.tw:35353")


def contribute(r: bytes):
    return client.contribute(r)


def eval(contribution):
    return client.get_verified_randomness(contribution, contribution.stage + 5)

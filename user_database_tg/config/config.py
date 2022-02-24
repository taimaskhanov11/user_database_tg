from environs import Env

env = Env()
env.read_env()

TG_TOKEN = env.str("TG_TOKEN")
QIWI_TOKEN= env.str("QIWI_TOKEN")
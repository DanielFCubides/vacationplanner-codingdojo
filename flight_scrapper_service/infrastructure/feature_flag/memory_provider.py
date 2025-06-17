from openfeature.provider.in_memory_provider import InMemoryFlag

#Flags
WELCOME_MESSAGE_FLAG = "welcome message on"


#Flags definition
my_flags = {
  WELCOME_MESSAGE_FLAG: InMemoryFlag("off", {"on": True, "off": False})
}

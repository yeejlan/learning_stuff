
from pathlib import Path

path = Path("app/user/userget-user-info")

# module_name = path.parent.name + "." + path.parts[-2]
# function_name = "_".join(path.name.split("-")) + "_action" 

controller = ".".join(path.parts[:3])
print(path.parts)
print(len(path.parts))
print(path.parts[0])

print(controller)
# print(module_name)
# # app.user

# print(function_name)  
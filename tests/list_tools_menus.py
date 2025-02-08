import unreal

def list_menu(num=1000):
    menu_list = set()  # remove duplicates when adding to set compared to list
    for i in range(num):
        obj = unreal.find_object(None, f"/Engine/Transient.ToolMenus_0:RegisteredMenu_{i}")
        if not obj:
            obj = unreal.find_object(None, f"/Engine/Transient.ToolMenus_0:ToolMenu_{i}")  # for UE4
        print(obj)
    #     menu_name = str(obj.menu_name)
    #     menu_list.add(menu_name)
    # return list(menu_list)

list_menu()
import vk


class VKWrapper:
    def __init__(self, vk_token, version="5.89"):
        session = vk.Session(access_token=vk_token)
        self.__vk_api = vk.API(session, v=version)

    def get_id_by_user(self, user: str):
        """
        :param user: или ссылка на страницу пользователя или имя(screen_name)
        :return:id
        """
        screen_name = user.lower().split("/")[-1]
        result = self.__vk_api.utils.resolveScreenName(screen_name=screen_name)
        if result is None or result["type"] != "user":
            return None
        return result["object_id"]

    def get_user_info(self, user: str, fields=None):
        id = self.get_id_by_user(user)
        return self.get_user_info_by_id(id, fields)

    def get_user_info_by_id(self, user_id, fields=None):
        if fields is None:
            return self.__vk_api.users.get(user_ids=user_id)[0]
        user_info = self.__vk_api.users.get(user_id=user_id, fields=fields, lang="ru")[0]

        if "career" in fields and "career" in user_info:
            if "group_id" not in user_info["career"][-1]:
                company_info = user_info["career"][-1]
            else:
                group_id = user_info["career"][-1]["group_id"]
                company_info = self.get_group_by_id(group_id)
            user_info["company_info"] = company_info

        return user_info

    def get_group_by_id(self, group_id):
        return self.__vk_api.groups.getById(group_id=group_id)[0]

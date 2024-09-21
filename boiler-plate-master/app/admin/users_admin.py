from sqladmin import ModelAdmin

from app.models.users import Users


class UserAdmin(ModelAdmin, model=Users):
    column_list = [Users.id, Users.code, Users.first_name, Users.middle_name, Users.last_name,
                   Users.phone_number, Users.email]

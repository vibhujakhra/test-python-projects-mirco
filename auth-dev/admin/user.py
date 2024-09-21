from sqladmin import ModelAdmin

from db.models.rbac import User


class UserAdmin(ModelAdmin, model=User):
    column_list = [User.id, User.email, User.role_id]

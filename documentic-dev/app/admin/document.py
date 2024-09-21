from sqladmin import ModelAdmin

from app.models.generate_policy import Templates, DocType, DocumentStatus


class TemplateAdmin(ModelAdmin, model=Templates):
    column_list = [Templates.id, Templates.insurer_code,
                   Templates.created_at, Templates.modified_at]


class DocumentStatusAdmin(ModelAdmin, model=DocumentStatus):
    column_list = [DocumentStatus.id, DocumentStatus.transaction_id,
                   DocumentStatus.created_at, DocumentStatus.modified_at,
                   DocumentStatus.url]


class DocTypeAdmin(ModelAdmin, model=DocType):
    column_list = [DocType.id, DocType.name]

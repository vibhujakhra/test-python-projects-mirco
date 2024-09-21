from sqladmin import ModelAdmin

from app.models.communication import CommunicationRequest, Templates


class CommunicationRequestAdmin(ModelAdmin, model=CommunicationRequest):
    column_list = [CommunicationRequest.id, CommunicationRequest.raw_request, CommunicationRequest.raw_response,
                   CommunicationRequest.worker_id, CommunicationRequest.templates_id, CommunicationRequest.status]


class TemplatesAdmin(ModelAdmin, model=Templates):
    column_list = [Templates.id, Templates.template_slug, Templates.email_template, Templates.whatsapp_template,
                   Templates.sms_template, Templates.is_dlt_approved, Templates.dlt_template_id, Templates.is_active]

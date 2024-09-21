from sqladmin import ModelAdmin

from app.models.payment import *


class PaymentStateAdmin(ModelAdmin, model=PaymentState):
    column_list = [PaymentState.id, PaymentState.name, PaymentState.code]


class PaymentModeAdmin(ModelAdmin, model=PaymentMode):
    column_list = [PaymentMode.id, PaymentMode.name, PaymentMode.code]


class ConsentTypeAdmin(ModelAdmin, model=ConsentType):
    column_list = [ConsentType.id, ConsentType.name]


class ConsentStateAdmin(ModelAdmin, model=ConsentState):
    column_list = [ConsentState.id, ConsentState.name]


class ConsentAdmin(ModelAdmin, model=Consent):
    column_list = [Consent.id, Consent.consent_type, Consent.consent_state]


class PaymentAdmin(ModelAdmin, model=Payment):
    column_list = [Payment.id, Payment.transaction_id]


class ChequeDetailsAdmin(ModelAdmin, model=ChequeDetails):
    column_list = [ChequeDetails.id, ChequeDetails.cheque_number]


class VerificationLinkAdmin(ModelAdmin, model=VerificationLink):
    column_list = [VerificationLink.id, VerificationLink.consent_id]


class MandateFormAdmin(ModelAdmin, model=MandateForm):
    column_list = [MandateForm.id, MandateForm.consent_id]


class InsurerCallLogAdmin(ModelAdmin, model=InsurerCallLog):
    column_list = [InsurerCallLog.id, InsurerCallLog.payment_id]


class HistoryAdmin(ModelAdmin, model=History):
    column_list = [History.id, History.class_name]


class BillingAdmin(ModelAdmin, model=Billing):
    column_list = [Billing.id, Billing.insurer_code, Billing.cheque_id]


class VB64Admin(ModelAdmin, model=VB64):
    column_list = [VB64.id, VB64.vb64_type_id, VB64.uploaded_by, VB64.upload_date, VB64.file_location]


class VB64RecordAdmin(ModelAdmin, model=VB64Record):
    column_list = [VB64Record.id, VB64Record.vb64_id]


class PaymentStatusAdmin(ModelAdmin, model=PaymentStatus):
    column_list = [PaymentStatus.id, PaymentStatus.name, PaymentStatus.code]


class PayInSlipAdmin(ModelAdmin, model=PayInSlip):
    column_list = [PayInSlip.id, PayInSlip.slip_number, PayInSlip.insurer_code, PayInSlip.download_url]

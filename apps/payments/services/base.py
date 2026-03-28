class BasePaymentService:
    def charge(self, amount, user):
        raise NotImplementedError
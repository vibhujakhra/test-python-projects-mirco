class Adaptor(object):
    """Base adaptor interface"""
    name = "Premiun Calculator Service"

    def compute_premium(self, query_details):
        """Returns the premium details with (atleast) the following data:

            {
            }
        """
        raise NotImplementedError("Should be implemented by the adaptor")

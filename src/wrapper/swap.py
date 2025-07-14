from base_wrapper import BaseWrapper

class Note(BaseWrapper):
    """
    Wrapper class for a fixed-rate bond or note.

    Attributes:
        face_value (float): Principal amount repaid at maturity.
        coupon_rate (float): Annual coupon rate (e.g., 0.05 for 5%).
        years_to_maturity (int): Number of years until maturity.

    Example:
        Note(face_value=1000, coupon_rate=0.05, years_to_maturity=3)
    """

    def __init__(self, face_value: float, coupon_rate: float, years_to_maturity: int):
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.years_to_maturity = years_to_maturity

    def price(self, discount_rate=0.03):
        """
        Calculate the present value of the bond using a fixed discount rate.

        Arguments:
            discount_rate (float): Annual discount rate used for present value.

        Returns:
            float: Present value = PV(coupons) + PV(face value)
        """
        coupons = self.coupon_rate * self.face_value
        pv_coupons = coupons * ((1 - (1 + discount_rate) ** -self.years_to_maturity) / discount_rate)
        pv_face = self.face_value / ((1 + discount_rate) ** self.years_to_maturity)
        return pv_coupons + pv_face
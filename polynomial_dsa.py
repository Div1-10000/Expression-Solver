import re

#
# --- DATA STRUCTURE DEFINITIONS (DSA) ---
#

class Term:
    """
    Node in a linked list representing a single term of a polynomial.
    """
    def __init__(self, coeff=0.0, power=0.0):
        self.coeff = coeff
        self.power = power
        self.next = None


class Polynomial:
    """
    A polynomial represented as a linked list of Term nodes.
    """
    def __init__(self):
        self.head = None

    def insertTerm(self, coeff, power):
        if abs(coeff) < 1e-9:
            return
        new_term = Term(coeff, power)
        new_term.next = self.head
        self.head = new_term

    def to_string(self, constant_term=""):
        if self.head is None:
            return "0" + constant_term

        terms = []
        current = self.head
        while current:
            terms.append(current)
            current = current.next

        # Sort by power descending
        terms.sort(key=lambda t: t.power, reverse=True)

        output = ""
        is_first_term = True
        for term in terms:
            coeff, power = term.coeff, term.power
            if abs(coeff) < 1e-9:
                continue

            sign = " + " if coeff > 0 else " - "
            coeff = abs(coeff)

            if is_first_term:
                output += "-" if sign == " - " else ""
            else:
                output += sign

            coeff_str = f"{coeff:.2f}".rstrip('0').rstrip('.')

            if coeff_str != "1" or power == 0:
                output += coeff_str

            if power > 0:
                if coeff_str == "1" and power > 0 and not is_first_term and output[-len(coeff_str):] == coeff_str:
                    output = output[:-len(coeff_str)]  # remove "1" for x terms
                output += "x"
                if power != 1:
                    power_str = f"{int(power) if power.is_integer() else power}"
                    output += f"^{power_str}"

            is_first_term = False

        return output + constant_term if output else "0" + constant_term

    def simplify(self):
        terms_map = {}
        current = self.head
        while current:
            terms_map[current.power] = terms_map.get(current.power, 0) + current.coeff
            current = current.next

        self.head = None
        for power, coeff in terms_map.items():
            self.insertTerm(coeff, power)

    #
    # --- POLYNOMIAL OPERATIONS ---
    #

    def add(self, other):
        result_map = self.to_term_map()
        other_map = other.to_term_map()
        for p, c in other_map.items():
            result_map[p] = result_map.get(p, 0) + c
        return Polynomial.from_term_map(result_map)

    def subtract(self, other):
        result_map = self.to_term_map()
        other_map = other.to_term_map()
        for p, c in other_map.items():
            result_map[p] = result_map.get(p, 0) - c
        return Polynomial.from_term_map(result_map)

    def multiply(self, other):
        result_map = {}
        current_a = self.head
        while current_a:
            current_b = other.head
            while current_b:
                power = current_a.power + current_b.power
                coeff = current_a.coeff * current_b.coeff
                result_map[power] = result_map.get(power, 0) + coeff
                current_b = current_b.next
            current_a = current_a.next
        return Polynomial.from_term_map(result_map)

    def differentiate(self):
        result = Polynomial()
        current = self.head
        while current:
            if current.power > 0:
                result.insertTerm(current.coeff * current.power, current.power - 1)
            current = current.next
        return result

    def integrate(self):
        result = Polynomial()
        current = self.head
        while current:
            result.insertTerm(current.coeff / (current.power + 1), current.power + 1)
            current = current.next
        return result

    def evaluate(self, x_val):
        x_val = float(x_val)
        total = 0.0
        current = self.head
        while current:
            total += current.coeff * (x_val ** current.power)
            current = current.next
        return total

    def divide(self, divisor):
        dividend_map = self.to_term_map()
        divisor_map = divisor.to_term_map()
        quotient_map = {}

        def get_lead_term(m):
            if not m: return (0, 0)
            max_pow = max(m.keys())
            return (m[max_pow], max_pow)

        lead_divisor = get_lead_term(divisor_map)
        if lead_divisor[0] == 0:
            raise ValueError("Cannot divide by zero polynomial.")

        while dividend_map:
            lead_dividend = get_lead_term(dividend_map)
            if lead_dividend[1] < lead_divisor[1]:
                break
            q_power = lead_dividend[1] - lead_divisor[1]
            q_coeff = lead_dividend[0] / lead_divisor[0]
            quotient_map[q_power] = q_coeff

            # Subtract (quotient_term * divisor) from dividend
            for d_power, d_coeff in divisor_map.items():
                sub_power = d_power + q_power
                sub_coeff = d_coeff * q_coeff
                dividend_map[sub_power] = dividend_map.get(sub_power, 0) - sub_coeff
                if abs(dividend_map[sub_power]) < 1e-9:
                    del dividend_map[sub_power]

        quotient_poly = Polynomial.from_term_map(quotient_map)
        remainder_poly = Polynomial.from_term_map(dividend_map)
        return quotient_poly, remainder_poly

    #
    # --- HELPERS ---
    #

    def to_term_map(self):
        m = {}
        current = self.head
        while current:
            if abs(current.coeff) > 1e-9:
                m[current.power] = m.get(current.power, 0) + current.coeff
            current = current.next
        return m

    @staticmethod
    def from_term_map(m):
        poly = Polynomial()
        for p, c in m.items():
            poly.insertTerm(c, p)
        return poly

#
# --- PARSER ---
#

TERM_REGEX = re.compile(r"([+-]?\s*\d*\.?\d*)\s*x(?:\^(\d*\.?\d*))?|([+-]?\s*\d+\.?\d*)")

def parse_string_to_poly(poly_string):
    poly = Polynomial()
    s = poly_string.replace("-x", "-1x").replace("+x", "+1x")
    if s.strip().startswith("x"):
        s = "1" + s

    for match in TERM_REGEX.finditer(s):
        coeff_str, power_str, const_str = match.groups()
        try:
            if const_str:  # constant term
                coeff = float(const_str.replace(" ", ""))
                poly.insertTerm(coeff, 0)
            else:  # term with x
                coeff = float(coeff_str.replace(" ", "")) if coeff_str not in ("", "+", "-") else (1.0 if coeff_str in ("", "+") else -1.0)
                power = float(power_str) if power_str else 1.0
                poly.insertTerm(coeff, power)
        except ValueError:
            continue

    poly.simplify()
    return poly

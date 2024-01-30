import copy
from datetime import datetime
from tabulate import tabulate

from common.variables import MAX_401K_AND_ROTH_CONTRIBUTION


class RetirementPlanner:
    def __init__(self, *arg):
        self.user_data = arg
        self.compounded_table = []
        self.annual_contribution = 0.0
        self.total_contribution = 0.0
        self.interest_earned_per_year = 0.0
        self.total_interest_earned = 0.0
        self.total_end_balance = 0.0
        self.year = 0
        self.age = 0
        self.name = ""
        self.combined_table = []
        self.total_company_contributions = 0.0
        self.payday_contribution = 0

        for user in arg:
            self.payday_contribution = user["per_payday_contribution"]
            self.name = user["name"]
            self.total_end_balance = user["starting_amount"]
            self.build_chart(user)
            self.print_chart(copy.deepcopy(self.compounded_table), self.name)
            self.combined_table.append(copy.deepcopy(self.compounded_table))
            self.compounded_table.clear()
            self.total_interest_earned = 0.0
            self.total_contribution = 0.0

        self.combine()

    def combine(self):
        formatted_table = []
        temp_fill = [0, 0, 0, 0, 0, 0, 0, 0]

        for count, data in enumerate(self.combined_table):
            for count2, single_data in enumerate(data):
                if count == 0:
                    formatted_table.append(copy.deepcopy(temp_fill))
                    formatted_table[count2][0] = data[count2][0]
                    formatted_table[count2][1] = data[count2][1]
                    for num in range(2, len(single_data)):
                        formatted_table[count2][num] += single_data[num]
                else:
                    for num in range(2, len(single_data)):
                        formatted_table[count2][num] += single_data[num]
        self.print_chart(formatted_table, "Combined")

    def set_year_and_age(self, num_of_years, age):
        # Set the year
        if num_of_years == 0:
            self.age = age
            self.year = int(datetime.today().strftime('%Y-%m-%d')[0:4])
        else:
            self.age += 1
            self.year += 1

    def calculate_company_contribution(self, single_user_data):
        self.total_company_contributions = self.convert_pay_schedule(single_user_data["company_match_pay_schedule"]) * \
                                           single_user_data["company_match"]

    def set_annual_contribution(self, num_of_years, single_user_data):
        # Set annual contribution
        if num_of_years == 0:
            self.calculate_company_contribution(single_user_data)

            self.annual_contribution = self.payday_contribution * self.convert_pay_schedule(
                single_user_data["pay_schedule"])

        update = self.payday_contribution + (
                    self.payday_contribution * (single_user_data["yearly_income_growth"] / 100))
        self.payday_contribution = update

        if self.annual_contribution + update >= MAX_401K_AND_ROTH_CONTRIBUTION and "BROKERAGE" not in single_user_data[
            "name"].upper():
            self.annual_contribution = MAX_401K_AND_ROTH_CONTRIBUTION
        else:
            self.annual_contribution += update

        self.total_contribution += self.annual_contribution + self.total_company_contributions
        return self.annual_contribution

    def build_chart(self, single_user_data):
        for num_of_years in range(0, int(single_user_data["years_to_grow"])):
            # Set the year
            self.set_year_and_age(num_of_years, single_user_data["age"])

            # Set annual contribution
            annual_contribution = self.set_annual_contribution(num_of_years, single_user_data)

            # Set balance
            self.interest_earned_per_year = ((self.total_end_balance + annual_contribution) * (
                        single_user_data["percentage_rate_of_return"] / 100))
            self.total_interest_earned += self.interest_earned_per_year
            self.total_end_balance += annual_contribution + self.interest_earned_per_year + self.total_company_contributions

            self.compounded_table.append([self.age, self.year, annual_contribution, self.total_company_contributions, self.total_contribution,
                                          self.interest_earned_per_year, self.total_interest_earned,
                                          self.total_end_balance])

    def convert_pay_schedule(self, pay_schedule):
        match pay_schedule:
            case "MONTHLY":
                pay_per_year = 12
            case "ANNUALLY":
                pay_per_year = 1
            case "SEMI-MONTHLY":
                pay_per_year = 24
            case "BI-WEEKLY":
                pay_per_year = 26
            case _:  # Default
                pay_per_year = 12
        return pay_per_year

    def build_title(self, name):
        build_string = f" {name}'s Retirement Breakdown "
        string_length = 141
        left_right = "left"

        while string_length != len(build_string):
            if left_right == "left":
                build_string = f"*{build_string}"
                left_right = "right"
            else:
                build_string = f"{build_string}*"
                left_right = "left"

        print(f"\n{build_string}")

    def print_chart(self, table, name):
        table = (x for x in table)
        self.build_title(name)
        print(
            tabulate(
                table,
                headers=["Age", "Year", "Annual Contribution", "Company Contributions", "Total Contributions",
                         "Rate of Return", "Total Rate of Return", "End Balance"],
                floatfmt=",.2f",
                numalign="right"
            )
        )


if __name__ == "__main__":
    years_to_grow = 26
    test = RetirementPlanner(
        {
            "name": "Dan",
            "age": 35,
            "yearly_income_growth": 5,
            "starting_amount": 40977.20,
            "company_match": 3450,
            "company_match_pay_schedule": "ANNUALLY",
            "per_payday_contribution": 718.75,
            "pay_schedule": "SEMI-MONTHLY",
            "percentage_rate_of_return": 10,
            "years_to_grow": years_to_grow,
        },
        {
            "name": "Lara",
            "age": 33,
            "yearly_income_growth": 2,
            "starting_amount": 5005,
            "company_match": 10.60,
            "company_match_pay_schedule": "BI-WEEKLY",
            "per_payday_contribution": 317.95,
            "pay_schedule": "BI-WEEKLY",
            "percentage_rate_of_return": 10,
            "years_to_grow": years_to_grow,
        },
        {
            "name": "Joint Savings",
            "age": 35,
            "yearly_income_growth": 0,
            "company_match": 0,
            "company_match_pay_schedule": "ANNUALLY",
            "starting_amount": 15000,
            "per_payday_contribution": 0,
            "pay_schedule": "MONTHLY",
            "percentage_rate_of_return": 0,
            "years_to_grow": years_to_grow,
        },
        {
            "name": "Joint Brokerage",
            "age": 35,
            "yearly_income_growth": 5,
            "company_match": 750.00, # From 5% High performance savings every year
            "company_match_pay_schedule": "ANNUALLY",
            "starting_amount": 3207.45,
            "per_payday_contribution": 1585.64,
            "pay_schedule": "MONTHLY",
            "percentage_rate_of_return": 12,
            "years_to_grow": years_to_grow,
        },
    )

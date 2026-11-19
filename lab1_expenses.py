import math
from datetime import date

TAX_RATE = 0.18
PASS_MARK = 35
ELIGIBLE_LIMIT = 75
WARNING_LIMIT = 60
STOP_WORD = "done"

CATEGORIES = ["Food", "Travel", "Utilities", "Stationery", "Other"]
DEFAULT_SUBJECT_NAMES = ["Maths", "Science", "English", "History", "Computer"]

expenses = []
people = []
students = []
bills = []

settings = {
    "total_days": None,
    "subjects": ["Maths", "Science", "English", "History", "Computer"],
}


def get_int(prompt, min_val=0, max_val=None, error="Enter a whole number."):
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print(error)
            continue
        if value < min_val:
            print(error)
            continue
        if max_val is not None and value > max_val:
            print(error)
            continue
        return value


def get_float(prompt, min_val=0.0, max_val=1000000000.0, error="Invalid number."):
    while True:
        text = input(prompt).strip()
        try:
            value = float(text)
        except ValueError:
            print(error)
            continue
        if not math.isfinite(value):
            print(error)
            continue
        if value < min_val or value > max_val:
            print(error)
            continue
        return value


def get_name(prompt):
    while True:
        name = input(prompt).strip()
        name = " ".join(name.split())
        letter_count = 0
        all_valid = True
        for ch in name:
            if ch.isalpha():
                letter_count = letter_count + 1
            elif ch != " ":
                all_valid = False
        if all_valid and letter_count >= 2 and len(name) <= 40:
            return name
        print("Name must contain 2-40 letters.")


def get_text(prompt, error, max_len=40):
    while True:
        text = input(prompt).strip()
        text = " ".join(text.split())
        if text != "" and len(text) <= max_len:
            return text
        print(error)


def get_choice(prompt, options):
    while True:
        text = input(prompt).strip().lower()
        for option in options:
            if option.lower() == text:
                return option
        print("Choose a category from the list.")


def get_yes_no(prompt):
    while True:
        text = input(prompt).strip().lower()
        if text == "y" or text == "yes":
            return True
        if text == "n" or text == "no":
            return False
        print("Please type yes or no.")


def get_menu_choice(low, high):
    message = "Invalid choice. Enter " + str(low) + "-" + str(high) + "."
    return get_int("Enter your choice (" + str(low) + "-" + str(high) + "): ",
                   low, high, message)


def show(text):
    print()
    if text is None:
        print("No records available.")
    else:
        print(text)


def add_expense():
    description = get_text("Description: ", "Description cannot be empty.")
    category = get_choice("Category (" + "/".join(CATEGORIES) + "): ", CATEGORIES)
    amount = get_float("Amount: ", 0.01, 1000000000.0,
                       "Amount must be a positive number.")
    expense = {
        "description": description,
        "category": category,
        "amount": round(amount, 2),
    }
    expenses.append(expense)
    print("Expense added successfully!")


def get_category_totals():
    totals = {}
    for expense in expenses:
        category = expense["category"]
        if category not in totals:
            totals[category] = 0
        totals[category] = totals[category] + expense["amount"]
    return totals


def expense_list():
    if len(expenses) == 0:
        return None
    lines = []
    lines.append("=== ALL EXPENSES ===")
    lines.append(f"{'No':<4}{'Description':<25}{'Category':<12}{'Amount':>12}")
    lines.append("-" * 53)
    number = 1
    for expense in expenses:
        lines.append(f"{number:<4}{expense['description']:<25}"
                     f"{expense['category']:<12}{expense['amount']:>12.2f}")
        number = number + 1
    return "\n".join(lines)


def expense_summary():
    if len(expenses) == 0:
        return None
    totals = get_category_totals()
    lines = []
    lines.append("=== EXPENSE SUMMARY ===")
    lines.append(f"{'CATEGORY':<15}{'TOTAL':>12}")
    for category in CATEGORIES:
        if category in totals:
            lines.append(f"{category:<15}{totals[category]:>12.2f}")
    lines.append("-" * 27)

    grand_total = 0
    highest = expenses[0]
    lowest = expenses[0]
    for expense in expenses:
        grand_total = grand_total + expense["amount"]
        if expense["amount"] > highest["amount"]:
            highest = expense
        if expense["amount"] < lowest["amount"]:
            lowest = expense
    grand_total = round(grand_total, 2)

    lines.append(f"{'GRAND TOTAL':<15}{grand_total:>12.2f}")
    lines.append(f"Highest expense: {highest['description']} "
                 f"({highest['category']}) - {highest['amount']:.2f}")
    lines.append(f"Lowest expense : {lowest['description']} "
                 f"({lowest['category']}) - {lowest['amount']:.2f}")
    return "\n".join(lines)


def expense_report():
    if len(expenses) == 0:
        return None
    return expense_list() + "\n\n" + expense_summary()


def expense_menu():
    while True:
        print("\n--- EXPENSE MANAGEMENT ---")
        print(" 1. Add Expense")
        print(" 2. View All Expenses")
        print(" 3. Expense Summary")
        print(" 4. Back")
        choice = get_menu_choice(1, 4)
        if choice == 1:
            add_expense()
        elif choice == 2:
            show(expense_list())
        elif choice == 3:
            show(expense_summary())
        else:
            return


def attendance_percentage(present, total_days):
    if total_days <= 0:
        return 0.0
    return round(present / total_days * 100, 2)


def attendance_status(percentage):
    if percentage >= ELIGIBLE_LIMIT:
        return "Eligible"
    elif percentage >= WARNING_LIMIT:
        return "Warning"
    else:
        return "Shortage"


def set_total_days():
    lowest_allowed = 1
    for person in people:
        if person["present"] > lowest_allowed:
            lowest_allowed = person["present"]
    message = "Enter a whole number of at least " + str(lowest_allowed) + "."
    settings["total_days"] = get_int("Total working days: ",
                                     lowest_allowed, None, message)
    print("Working days saved.")


def id_already_used(person_id):
    for person in people:
        if person["id"].lower() == person_id.lower():
            return True
    return False


def mark_attendance():
    if settings["total_days"] is None:
        print("Set the total working days first.")
        set_total_days()
    total = settings["total_days"]

    name = get_name("Name: ")

    while True:
        person_id = get_text("ID: ", "ID cannot be empty (max 10 characters).", 10)
        if not person_id.isalnum():
            print("ID can only have letters and numbers.")
        elif id_already_used(person_id):
            print("That ID is already recorded.")
        else:
            break

    message = "Days present must be between 0 and " + str(total) + "."
    present = get_int("Days present (0-" + str(total) + "): ", 0, total, message)

    person = {"name": name, "id": person_id, "present": present}
    people.append(person)
    print("Attendance recorded.")


def attendance_table():
    if len(people) == 0:
        return None
    total = settings["total_days"]
    lines = []
    lines.append("=== ATTENDANCE ===")
    lines.append(f"{'Name':<22}{'ID':<10}{'Total Days':>11}{'Present':>9}"
                 f"{'Attendance %':>14}  Status")
    lines.append("-" * 77)
    for person in people:
        percentage = attendance_percentage(person["present"], total)
        status = attendance_status(percentage)
        lines.append(f"{person['name']:<22}{person['id']:<10}{total:>11}"
                     f"{person['present']:>9}{percentage:>14.2f}  {status}")
    return "\n".join(lines)


def attendance_summary():
    if len(people) == 0:
        return None
    total = settings["total_days"]

    percentage_sum = 0
    eligible_count = 0
    warning_count = 0
    shortage_count = 0
    best_person = people[0]
    worst_person = people[0]
    best_percentage = attendance_percentage(people[0]["present"], total)
    worst_percentage = best_percentage

    for person in people:
        percentage = attendance_percentage(person["present"], total)
        percentage_sum = percentage_sum + percentage

        if percentage > best_percentage:
            best_percentage = percentage
            best_person = person
        if percentage < worst_percentage:
            worst_percentage = percentage
            worst_person = person

        status = attendance_status(percentage)
        if status == "Eligible":
            eligible_count = eligible_count + 1
        elif status == "Warning":
            warning_count = warning_count + 1
        else:
            shortage_count = shortage_count + 1

    average = percentage_sum / len(people)

    lines = []
    lines.append("Summary:")
    lines.append(f"Total students     : {len(people)}")
    lines.append(f"Average attendance : {average:.2f}%")
    lines.append(f"Highest            : {best_person['name']} ({best_percentage:.2f}%)")
    lines.append(f"Lowest             : {worst_person['name']} ({worst_percentage:.2f}%)")
    lines.append(f"Eligible: {eligible_count} | Warning: {warning_count} "
                 f"| Shortage: {shortage_count}")
    return "\n".join(lines)


def attendance_report():
    if len(people) == 0:
        return None
    return attendance_table() + "\n\n" + attendance_summary()


def attendance_menu():
    while True:
        print("\n--- ATTENDANCE MANAGEMENT ---")
        print(" 1. Set Total Working Days")
        print(" 2. Add Person's Attendance")
        print(" 3. View Attendance and Summary")
        print(" 4. Back")
        choice = get_menu_choice(1, 4)
        if choice == 1:
            set_total_days()
        elif choice == 2:
            mark_attendance()
        elif choice == 3:
            show(attendance_report())
        else:
            return


def calculate_grade(percentage):
    if percentage >= 90:
        return "A+", "Outstanding"
    elif percentage >= 80:
        return "A", "Excellent"
    elif percentage >= 70:
        return "B", "Very Good"
    elif percentage >= 60:
        return "C", "Good"
    elif percentage >= 50:
        return "D", "Satisfactory"
    elif percentage >= 35:
        return "E", "Pass"
    else:
        return "F", "Fail"


def format_marks(value):
    if value == int(value):
        return str(int(value))
    return str(round(value, 2))


def set_subject_count():
    if len(students) > 0:
        print("Subjects can't be changed after students have been entered.")
        return

    count = get_int("Number of subjects (1-15): ", 1, 15,
                    "Enter a whole number between 1 and 15.")
    names = []
    for i in range(count):
        if i < len(DEFAULT_SUBJECT_NAMES):
            default_name = DEFAULT_SUBJECT_NAMES[i]
        else:
            default_name = "Subject " + str(i + 1)
        typed = input("Name of subject " + str(i + 1) + " [" + default_name + "]: ")
        typed = typed.strip()
        if typed == "":
            names.append(default_name)
        else:
            names.append(typed)
    settings["subjects"] = names
    print(str(count) + " subjects saved.")


def add_student():
    name = get_name("Student name: ")

    marks = []
    for subject in settings["subjects"]:
        mark = get_float("Marks in " + subject + " (0-100): ", 0, 100,
                         "Marks must be between 0 and 100.")
        marks.append(mark)

    total = 0
    failed = False
    for mark in marks:
        total = total + mark
        if mark < PASS_MARK:
            failed = True

    maximum = 100 * len(marks)
    average = total / len(marks)
    percentage = round(total / maximum * 100, 2)
    grade, remark = calculate_grade(percentage)

    if failed:
        result = "FAIL"
    else:
        result = "PASS"

    student = {
        "name": name,
        "marks": marks,
        "total": total,
        "maximum": maximum,
        "average": round(average, 2),
        "percentage": percentage,
        "grade": grade,
        "result": result,
    }
    students.append(student)
    print("Student added.")
    print(generate_report_card(student))


def generate_report_card(student):
    lines = []
    lines.append("=========== REPORT CARD ===========")
    lines.append("Student : " + student["name"])
    lines.append("-" * 35)
    lines.append(f"{'Subject':<15}{'Marks':>8}")

    position = 0
    for subject in settings["subjects"]:
        mark = student["marks"][position]
        lines.append(f"{subject:<15}{format_marks(mark):>8}")
        position = position + 1

    lines.append("-" * 35)
    lines.append("Total      : " + format_marks(student["total"])
                 + " / " + str(student["maximum"]))
    lines.append(f"Average    : {student['average']:.2f}")
    lines.append(f"Percentage : {student['percentage']:.2f}%")
    lines.append("Grade      : " + student["grade"])
    lines.append("Result     : " + student["result"])
    lines.append("=" * 35)
    return "\n".join(lines)


def class_summary():
    if len(students) == 0:
        return None

    percentage_sum = 0
    passed_count = 0
    topper = students[0]
    for student in students:
        percentage_sum = percentage_sum + student["percentage"]
        if student["result"] == "PASS":
            passed_count = passed_count + 1
        if student["percentage"] > topper["percentage"]:
            topper = student

    count = len(students)
    class_average = percentage_sum / count

    lines = []
    lines.append("=== CLASS SUMMARY ===")
    lines.append(f"{'Name':<22}{'Percentage':>11}{'Grade':>7}  Result")
    lines.append("-" * 50)
    for student in students:
        lines.append(f"{student['name']:<22}{student['percentage']:>11.2f}"
                     f"{student['grade']:>7}  {student['result']}")
    lines.append("-" * 50)
    lines.append(f"Students      : {count}")
    lines.append(f"Class average : {class_average:.2f}%")
    lines.append(f"Topper        : {topper['name']} ({topper['percentage']:.2f}%)")
    lines.append(f"Passed: {passed_count} | Failed: {count - passed_count}")
    return "\n".join(lines)


def grading_report():
    if len(students) == 0:
        return None
    cards = []
    for student in students:
        cards.append(generate_report_card(student))
    return "\n\n".join(cards) + "\n\n" + class_summary()


def grading_menu():
    while True:
        print("\n--- GRADING SYSTEM ---")
        print(" 1. Add Student Marks")
        print(" 2. View Class Summary")
        print(" 3. Change Subjects")
        print(" 4. Back")
        choice = get_menu_choice(1, 4)
        if choice == 1:
            add_student()
        elif choice == 2:
            show(class_summary())
        elif choice == 3:
            set_subject_count()
        else:
            return


def calculate_discount(subtotal):
    if subtotal >= 10000:
        return 0.15
    elif subtotal >= 5000:
        return 0.10
    elif subtotal >= 1000:
        return 0.05
    else:
        return 0.0


def calculate_tax(taxable):
    return round(taxable * TAX_RATE, 2)


def create_bill():
    customer = get_name("Customer name: ")
    bill_no = "B-" + str(len(bills) + 1).zfill(4)
    print("Bill number: " + bill_no)
    print("Add items one by one. Type '" + STOP_WORD + "' as the item name to finish.")

    items = []
    while True:
        item_name = get_text("Item name: ", "Item name cannot be empty.")
        if item_name.lower() == STOP_WORD:
            break
        price = get_float("Unit price: ", 0.01, 1000000000.0,
                          "Price must be greater than 0.")
        quantity = get_int("Quantity: ", 1, None,
                           "Quantity must be a whole number >= 1.")
        price = round(price, 2)
        item = {
            "name": item_name,
            "price": price,
            "qty": quantity,
            "total": round(price * quantity, 2),
        }
        items.append(item)

    if len(items) == 0:
        print("No items added. Bill cancelled.")
        return

    subtotal = 0
    for item in items:
        subtotal = subtotal + item["total"]
    subtotal = round(subtotal, 2)

    rate = calculate_discount(subtotal)
    discount_amount = round(subtotal * rate, 2)
    taxable = round(subtotal - discount_amount, 2)
    tax_amount = calculate_tax(taxable)
    grand_total = round(taxable + tax_amount, 2)

    bill = {
        "bill_no": bill_no,
        "date": date.today().isoformat(),
        "customer": customer,
        "items": items,
        "subtotal": subtotal,
        "rate": rate,
        "discount": discount_amount,
        "taxable": taxable,
        "tax": tax_amount,
        "grand_total": grand_total,
    }
    bills.append(bill)
    print()
    print(generate_invoice(bill))


def generate_invoice(bill):
    discount_label = "Discount (" + format(bill["rate"] * 100, "g") + "%)"
    tax_label = "Tax (" + format(TAX_RATE * 100, "g") + "%)"
    negative_discount = -bill["discount"]

    lines = []
    lines.append("=============== INVOICE ===============")
    lines.append("Bill No : " + bill["bill_no"] + "    Date: " + bill["date"])
    lines.append("Customer : " + bill["customer"])
    lines.append("-" * 39)
    lines.append(f"{'Item':<15}{'Price':>8}{'Qty':>5}{'Total':>11}")
    for item in bill["items"]:
        short_name = item["name"][:14]
        lines.append(f"{short_name:<15}{item['price']:>8.2f}"
                     f"{item['qty']:>5}{item['total']:>11.2f}")
    lines.append("-" * 39)
    lines.append(f"{'Subtotal':<24}{bill['subtotal']:>15.2f}")
    lines.append(f"{discount_label:<24}{negative_discount:>15.2f}")
    lines.append(f"{'Taxable amount':<24}{bill['taxable']:>15.2f}")
    lines.append(f"{tax_label:<24}{bill['tax']:>15.2f}")
    lines.append("-" * 39)
    lines.append(f"{'GRAND TOTAL':<24}{bill['grand_total']:>15.2f}")
    lines.append("=" * 39)
    lines.append("Thank you for your purchase!")
    return "\n".join(lines)


def billing_report():
    if len(bills) == 0:
        return None
    lines = []
    lines.append("=== BILLING REPORT ===")
    lines.append(f"{'Bill No':<10}{'Date':<12}{'Customer':<22}{'Total':>12}")
    lines.append("-" * 56)
    sales = 0
    for bill in bills:
        lines.append(f"{bill['bill_no']:<10}{bill['date']:<12}"
                     f"{bill['customer']:<22}{bill['grand_total']:>12.2f}")
        sales = sales + bill["grand_total"]
    sales = round(sales, 2)
    lines.append("-" * 56)
    bills_label = "Bills: " + str(len(bills))
    lines.append(f"{bills_label:<44}{sales:>12.2f}")
    return "\n".join(lines)


def billing_menu():
    while True:
        print("\n--- BILLING SYSTEM ---")
        print(" 1. Create New Bill")
        print(" 2. View All Bills")
        print(" 3. Back")
        choice = get_menu_choice(1, 3)
        if choice == 1:
            create_bill()
        elif choice == 2:
            show(billing_report())
        else:
            return


def export_report(text, filename):
    try:
        file = open(filename, "w", encoding="utf-8")
        file.write(text + "\n")
        file.close()
        print("Report saved to " + filename)
    except OSError as error:
        print("Could not save the file: " + str(error))


def reports_menu():
    while True:
        print("\n--- REPORTS ---")
        print(" 1. Expense Report")
        print(" 2. Attendance Report")
        print(" 3. Grading Report")
        print(" 4. Billing Report")
        print(" 5. Back")
        choice = get_menu_choice(1, 5)

        if choice == 5:
            return

        if choice == 1:
            name = "expense"
            text = expense_report()
        elif choice == 2:
            name = "attendance"
            text = attendance_report()
        elif choice == 3:
            name = "grading"
            text = grading_report()
        else:
            name = "billing"
            text = billing_report()

        show(text)
        if text is not None:
            if get_yes_no("\nSave this report to a .txt file? (yes/no): "):
                export_report(text, name + "_report.txt")


def display_menu():
    print()
    print("=" * 46)
    print("  EXPENSE | ATTENDANCE | GRADING | BILLING")
    print("=" * 46)
    print(" 1. Expense Management")
    print(" 2. Attendance Management")
    print(" 3. Grading System")
    print(" 4. Billing System")
    print(" 5. View Reports")
    print(" 6. Exit")
    print("-" * 46)


def main():
    try:
        while True:
            display_menu()
            choice = get_menu_choice(1, 6)
            if choice == 1:
                expense_menu()
            elif choice == 2:
                attendance_menu()
            elif choice == 3:
                grading_menu()
            elif choice == 4:
                billing_menu()
            elif choice == 5:
                reports_menu()
            else:
                print("Thank you for using the system. Goodbye!")
                break
    except (KeyboardInterrupt, EOFError):
        print("\n\nInput stopped. Goodbye!")


if __name__ == "__main__":
    main()
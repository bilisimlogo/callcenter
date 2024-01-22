import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Create a database connection
conn = sqlite3.connect("call_center.db")
cursor = conn.cursor()

# Create a table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customer_issues (
        id INTEGER PRIMARY KEY,
        customer_name TEXT,
        issue_date TEXT,
        program_name TEXT,
        customer_email TEXT,
        customer_phone TEXT,
        issue_detail TEXT,
        status TEXT
    )
''')
conn.commit()


class CallCenterApp:
    def __init__(self):
        self.state = st.session_state
        if not hasattr(self.state, 'success'):
            self.state.success = False
        if not hasattr(self.state, 'edit_selected_issue'):
            self.state.edit_selected_issue = None

    def get_customer_issues(self):
        cursor.execute('SELECT * FROM customer_issues')
        issues = cursor.fetchall()

        # Kontrol edilmiş bir şekilde sütunlara erişim
        return [
            dict(
                id=issue[0],
                customer_name=issue[1],
                issue_date=issue[2],
                program_name=issue[3],
                customer_email=issue[4],
                customer_phone=issue[5],
                issue_detail=issue[6],
                status=issue[7] if len(issue) > 7 else None
            ) for issue in issues
        ]

    def add_customer_issue(self):
        st.header("Add Issue")

        customer_name = st.text_input("Customer Name")
        issue_date = st.date_input("Issue Date", value=datetime.now())
        program_name = st.text_input("Program Name")
        customer_email = st.text_input("Customer Email")
        customer_phone = st.text_input("Customer Phone")
        issue_detail = st.text_area("Issue Detail")
        status = st.selectbox("Status", ["Open", "Closed", "In Review"])

        if st.button("Save"):
            # Insert the new issue into the database
            cursor.execute('INSERT INTO customer_issues (customer_name, issue_date, program_name, customer_email, customer_phone, issue_detail, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (customer_name, issue_date.strftime("%Y-%m-%d"), program_name, customer_email, customer_phone, issue_detail, status))
            conn.commit()
            st.success("Issue successfully added.")

    def view_customer_issues(self):
        st.header("View Issues")

        issues = self.get_customer_issues()

        if not issues:
            st.warning("No issues found.")
            return

        # Display issues as a DataFrame
        df = pd.DataFrame(issues)

        # Filter by status
        selected_status = st.selectbox(
            "Filter by Status", ["All", "Open", "Closed"])
        if selected_status != "All":
            df = df[df['status'] == selected_status]

        # Display simplified table
        st.table(
            df[['id', 'customer_name', 'issue_date', 'program_name', 'status']])

        # Update status to "Completed" for selected "Open" issues
        if selected_status == "Open":
            selected_issues = st.multiselect(
                "Select Open Issues to Mark as Completed", df[df['status'] == 'Open']['id'])
            if st.button("Mark as Completed"):
                for issue_id in selected_issues:
                    cursor.execute(
                        'UPDATE customer_issues SET status=? WHERE id=?', ('Closed', issue_id))
                conn.commit()
                st.success("Selected issues marked as Completed.")

    def edit_customer_issue(self):
        issues = self.get_customer_issues()

        # Filter customer names and dates
        customer_names = list(set(issue['customer_name'] for issue in issues))
        selected_customer_name = st.selectbox(
            "Select Customer Name", customer_names)

        issue_dates = list(set(
            issue['issue_date'] for issue in issues if issue['customer_name'] == selected_customer_name))
        selected_issue_date = st.selectbox("Select Date", issue_dates)

        # Fetch issues that match the selected customer and date
        filtered_issues = [issue for issue in issues if issue['customer_name'] ==
                           selected_customer_name and issue['issue_date'] == selected_issue_date]

        if not filtered_issues:
            st.warning("No issues found for the selected customer and date.")
            return

        # Show selected issues
        selected_issue_index = st.selectbox(
            "Select the issue to edit", range(len(filtered_issues)))
        self.state.edit_selected_issue = filtered_issues[selected_issue_index]

        with st.form(key='edit_issue_form'):
            st.header("Edit Issue")

            edited_customer_name = st.text_input(
                "New Customer Name", value=self.state.edit_selected_issue['customer_name'])
            edited_issue_date = st.date_input("New Issue Date", value=datetime.strptime(
                self.state.edit_selected_issue['issue_date'], "%Y-%m-%d").date())
            edited_program_name = st.text_input(
                "New Program Name", value=self.state.edit_selected_issue['program_name'])
            edited_customer_email = st.text_input(
                "New Customer Email", value=self.state.edit_selected_issue['customer_email'])
            edited_customer_phone = st.text_input(
                "New Customer Phone", value=self.state.edit_selected_issue['customer_phone'])
            edited_issue_detail = st.text_area(
                "New Issue Detail", value=self.state.edit_selected_issue['issue_detail'])

            save_button = st.form_submit_button("Save")

            if save_button:
                # Update the issue details
                self.state.edit_selected_issue['customer_name'] = edited_customer_name
                self.state.edit_selected_issue['issue_date'] = edited_issue_date.strftime(
                    "%Y-%m-%d")
                self.state.edit_selected_issue['program_name'] = edited_program_name
                self.state.edit_selected_issue['customer_email'] = edited_customer_email
                self.state.edit_selected_issue['customer_phone'] = edited_customer_phone
                self.state.edit_selected_issue['issue_detail'] = edited_issue_detail

                # Update the issue in the database
                cursor.execute('UPDATE customer_issues SET customer_name=?, issue_date=?, program_name=?, customer_email=?, customer_phone=?, issue_detail=? WHERE id=?', (edited_customer_name,
                               edited_issue_date.strftime("%Y-%m-%d"), edited_program_name, edited_customer_email, edited_customer_phone, edited_issue_detail, self.state.edit_selected_issue['id']))
                conn.commit()
                self.state.success = True
                st.success("Issue successfully updated.")

    def page_selection_chart(self):
        st.header("Page Selection Chart")

        # Get distinct years and months from the database
        cursor.execute(
            'SELECT DISTINCT strftime("%Y", issue_date) AS year FROM customer_issues ORDER BY year DESC')
        available_years = [row[0] for row in cursor.fetchall()]

        selected_year = st.selectbox("Select Year", available_years)

        cursor.execute(
            'SELECT DISTINCT strftime("%m", issue_date) AS month FROM customer_issues ORDER BY month ASC')
        available_months = [row[0] for row in cursor.fetchall()]

        selected_month = st.selectbox("Select Month", available_months)

        # Get the total count of each status
        cursor.execute(
            'SELECT status, strftime("%Y-%m", issue_date) AS month, COUNT(*) FROM customer_issues GROUP BY status, month')
        status_counts = pd.DataFrame(cursor.fetchall(), columns=[
                                     'Status', 'Month', 'Count'])

        # Filter by selected year and month
        status_counts = status_counts[(
            status_counts['Month'] == f"{selected_year}-{selected_month}")]

        # Create a bar chart
        st.bar_chart(status_counts.pivot(
            index='Month', columns='Status', values='Count'))

        open_issue_count = status_counts[status_counts['Status'] == 'Open']['Count'].sum(
        )
        st.text(f"Open Issues: {open_issue_count}")

    def run(self):
        st.title("Call Center Application")

        # Page selection
        page = st.sidebar.radio("Page Selection", [
                                "Add Issue", "View Issues", "Edit Issue", "Page Selection Chart"])

        # Page Selection Chart
        if page == "Page Selection Chart":
            self.page_selection_chart()

        # Add Issue
        elif page == "Add Issue":
            self.add_customer_issue()

        # View Issues
        elif page == "View Issues":
            self.view_customer_issues()

        # Edit Issue
        elif page == "Edit Issue":
            st.header("Edit Issue")
            self.edit_customer_issue()


# Call the application
app = CallCenterApp()
app.run()

# Close the database connection
conn.close()

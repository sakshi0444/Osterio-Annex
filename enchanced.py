import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize session state variables if they don't exist
if 'patient_queue' not in st.session_state:
    st.session_state.patient_queue = pd.DataFrame({
        'Patient ID': range(1, 11),
        'Name': [
            'John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Davis',
            'Emma Wilson', 'David Lee', 'Sarah Miller', 'Michael Clark', 'Lisa Anderson'
        ],
        'Priority': [
            'High', 'High', 'High', 'Medium', 'Medium',
            'Medium', 'Low', 'Low', 'Low', 'Low'
        ],
        'Wait Time': [
            '15 mins', '20 mins', '25 mins', '30 mins', '35 mins',
            '40 mins', '45 mins', '50 mins', '55 mins', '60 mins'
        ],
        'Status': ['Waiting'] * 10,
        'Submission Time': [datetime.now()] * 10
    })

if 'xray_machines' not in st.session_state:
    st.session_state.xray_machines = pd.DataFrame({
        'Machine ID': [f'XR00{i}' for i in range(1, 8)],
        'Location': [
            'Floor 1, Room 101', 'Floor 2, Room 205', 'Floor 1, Room 110', 
            'Floor 3, Room 302', 'Floor 2, Room 210', 'Floor 1, Room 115', 
            'Floor 3, Room 310'
        ],
        'Status': ['Available', 'In Use', 'Available', 'Maintenance', 
                  'Available', 'Available', 'Available'],
        'Expected Available Time': [
            datetime.now(),
            datetime.now() + timedelta(minutes=30),
            datetime.now(),
            datetime.now() + timedelta(hours=2),
            datetime.now(),
            datetime.now(),
            datetime.now()
        ],
        'Assigned Patient': ['None'] * 7
    })

if 'approved_patients' not in st.session_state:
    st.session_state.approved_patients = pd.DataFrame(columns=[ 
        'Patient ID', 'Name', 'Priority', 'Machine ID', 'Start Time', 'Status'
    ])

if 'current_role' not in st.session_state:
    st.session_state.current_role = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Home"
if 'next_patient_id' not in st.session_state:
    st.session_state.next_patient_id = 11

def handle_patient_submission(name, priority):
    patient_id = st.session_state.next_patient_id
    st.session_state.next_patient_id += 1
    
    # Add to queue without trying immediate allocation
    new_patient = pd.DataFrame([{
        'Patient ID': patient_id,
        'Name': name,
        'Priority': priority,
        'Wait Time': '0 mins',
        'Status': 'Waiting',
        'Submission Time': datetime.now()
    }])
    
    # Define priority order
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    
    # Add new patient to queue
    st.session_state.patient_queue = pd.concat(
        [st.session_state.patient_queue, new_patient], 
        ignore_index=True
    )
    
    # Sort queue by priority and submission time
    st.session_state.patient_queue['priority_value'] = st.session_state.patient_queue['Priority'].map(priority_order)
    st.session_state.patient_queue = st.session_state.patient_queue.sort_values(
        by=['priority_value', 'Submission Time']
    ).drop('priority_value', axis=1)
    
    return True

def allocate_xray_machine(patient_id, name, priority):
    """Allocate available X-ray machine based on priority"""
    available_machines = st.session_state.xray_machines[
        st.session_state.xray_machines['Status'] == 'Available'
    ]
    
    if not available_machines.empty:
        machine = available_machines.iloc[0]
        machine_idx = machine.name
        
        # Update machine status
        st.session_state.xray_machines.at[machine_idx, 'Status'] = 'In Use'
        st.session_state.xray_machines.at[machine_idx, 'Expected Available Time'] = \
            datetime.now() + timedelta(minutes=30)
        st.session_state.xray_machines.at[machine_idx, 'Assigned Patient'] = name
        
        # Add to approved patients
        new_approved_patient = pd.DataFrame([{
            'Patient ID': patient_id,
            'Name': name,
            'Priority': priority,
            'Machine ID': machine['Machine ID'],
            'Start Time': datetime.now(),
            'Status': 'In Progress'
        }])
        st.session_state.approved_patients = pd.concat(
            [st.session_state.approved_patients, new_approved_patient], 
            ignore_index=True
        )
        
        return True
    return False

# Set page config
st.set_page_config(page_title="X-Ray Machine Tracking System", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        background-color: #008CBA;
        color: white;
        font-size: 16px;
        border-radius: 8px;
    }
    .stButton button:hover {
        background-color: #005f7a;
    }
    .tab-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    .tab-button {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .tab-button.active {
        background-color: #008CBA;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Tab navigation
def switch_tab(tab_name):
    st.session_state.current_tab = tab_name
    st.rerun()

# Custom tab navigation
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    if st.button("Home", key="home_tab"):
        switch_tab("Home")
with col2:
    if st.button("Staff Portal", key="staff_tab"):
        switch_tab("Staff Portal")
with col3:
    if st.button("Doctor Portal", key="doctor_tab"):
        switch_tab("Doctor Portal")
with col4:
    if st.button("Radiologist Portal", key="radiologist_tab"):
        switch_tab("Radiologist Portal")

# Display current tab content
if st.session_state.current_tab == "Home":
    st.title("Welcome to the X-Ray Machine Tracking System")
    st.write("Please select your role to proceed:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("### Patient Access", icon="📋")
        st.write("Check X-ray machine availability and estimated wait times.")
        if st.button("Access Staff Portal"):
            st.session_state.current_role = "staff"
            switch_tab("Staff Portal")
    
    with col2:
        st.warning("### Doctor Access", icon="🩺")
        st.write("Manage patient queue and monitor machine status.")
        if st.button("Access Doctor Portal"):
            st.session_state.current_role = "doctor"
            switch_tab("Doctor Portal")
    
    with col3:
        st.success("### Radiologist Access", icon="🩻")
        st.write("Review approved patients and oversee X-ray process.")
        if st.button("Access Radiologist Portal"):
            st.session_state.current_role = "radiologist"
            switch_tab("Radiologist Portal")

elif st.session_state.current_tab == "Staff Portal":
    if st.session_state.current_role != "staff":
        st.warning("Please select your role as Staff from the Home tab first.")
    else:
        st.title("Staff Portal")
        
        if st.sidebar.button("Logout"):
            st.session_state.current_role = None
            switch_tab("Home")
        
        st.header("X-Ray Machine Availability")
        
        status_filter = st.selectbox("Filter by Status:", ["All"] + list(st.session_state.xray_machines['Status'].unique()))
        
        filtered_machines = st.session_state.xray_machines
        if status_filter != "All":
            filtered_machines = filtered_machines[filtered_machines['Status'] == status_filter]
        
        for _, machine in filtered_machines.iterrows():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.subheader(f"Machine {machine['Machine ID']}")
                st.write(f"📍 Location: {machine['Location']}")
            
            with col2:
                status_color = "green" if machine['Status'] == "Available" else "red" if machine['Status'] == "In Use" else "orange"
                st.markdown(f"Status: <span style='color:{status_color}'>{machine['Status']}</span>", unsafe_allow_html=True)
                if machine['Status'] == "In Use":
                    st.write(f"Expected Available: {machine['Expected Available Time'].strftime('%H:%M')}")
            
            with col3:
                if machine['Status'] == "Available":
                    if st.button(f"Request Appointment for {machine['Machine ID']}", key=f"req_{machine['Machine ID']}"):
                        st.success(f"Appointment requested for {machine['Machine ID']}!")
            
            st.divider()

elif st.session_state.current_tab == "Doctor Portal":
    if st.session_state.current_role != "doctor":
        st.warning("Please select your role as Doctor from the Home tab first.")
    else:
        st.title("Doctor Portal")
        
        if st.sidebar.button("Logout"):
            st.session_state.current_role = None
            switch_tab("Home")
        
        # Add Patient Section with proper form handling
        with st.form(key="add_patient_form"):
            st.header("Add New Patient")
            name = st.text_input("Patient Name")
            priority = st.selectbox("Priority Level", ["High", "Medium", "Low"])
            submit_button = st.form_submit_button("Submit Patient")
            
            if submit_button:
                if name:  # Check if name is not empty
                    handle_patient_submission(name, priority)
                    st.success(f"Patient {name} added to queue with {priority} priority.")
                else:
                    st.error("Please enter a patient name.")
        
        # Display patient queue and status
        st.subheader("Current Patient Queue")
        if not st.session_state.patient_queue.empty:
            patient_queue = st.session_state.patient_queue[['Patient ID', 'Name', 'Priority', 'Status', 'Submission Time']]
            st.dataframe(patient_queue.style.apply(
                lambda x: ['background-color: #ffcccc' if x['Priority'] == 'High'
                         else 'background-color: #ffffcc' if x['Priority'] == 'Medium'
                         else 'background-color: #ccffcc' for _ in x],
                axis=1
            ))
        else:
            st.info("No patients in queue")

elif st.session_state.current_tab == "Radiologist Portal":
    if st.session_state.current_role != "radiologist":
        st.warning("Please select your role as Radiologist from the Home tab first.")
    else:
        st.title("Radiologist Portal")
        
        if st.sidebar.button("Logout"):
            st.session_state.current_role = None
            switch_tab("Home")
        
        # Machine Status Overview
        st.header("Machine Status Overview")
        cols = st.columns(4)
        
        # Calculate machine statistics
        total_machines = len(st.session_state.xray_machines)
        available_machines = sum(st.session_state.xray_machines['Status'] == 'Available')
        in_use_machines = sum(st.session_state.xray_machines['Status'] == 'In Use')
        maintenance_machines = sum(st.session_state.xray_machines['Status'] == 'Maintenance')
        
        cols[0].metric("Total Machines", total_machines)
        cols[1].metric("Available", available_machines)
        cols[2].metric("In Use", in_use_machines)
        cols[3].metric("Under Maintenance", maintenance_machines)
        
        # Machine Status Management
        st.subheader("Machine Status Management")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(st.session_state.xray_machines)
        
        with col2:
            with st.form("update_machine_status"):
                st.write("Update Machine Status")
                machine_id = st.selectbox(
                    "Select Machine",
                    options=st.session_state.xray_machines['Machine ID']
                )
                new_status = st.selectbox(
                    "New Status",
                    options=['Available', 'In Use', 'Maintenance']
                )
                if st.form_submit_button("Update Status"):
                    idx = st.session_state.xray_machines[
                        st.session_state.xray_machines['Machine ID'] == machine_id
                    ].index[0]
                    st.session_state.xray_machines.at[idx, 'Status'] = new_status
                    if new_status == 'Available':
                        st.session_state.xray_machines.at[idx, 'Expected Available Time'] = datetime.now()
                        st.session_state.xray_machines.at[idx, 'Assigned Patient'] = 'None'
                    st.success(f"Machine {machine_id} status updated to {new_status}")
                    st.rerun()
        
        # Queue Statistics
        st.header("Queue Statistics")
        queue_cols = st.columns(4)
        
        total_waiting = len(st.session_state.patient_queue)
        high_priority = sum(st.session_state.patient_queue['Priority'] == 'High')
        medium_priority = sum(st.session_state.patient_queue['Priority'] == 'Medium')
        low_priority = sum(st.session_state.patient_queue['Priority'] == 'Low')
        
        queue_cols[0].metric("Total Waiting", total_waiting)
        queue_cols[1].metric("High Priority", high_priority)
        queue_cols[2].metric("Medium Priority", medium_priority)
        queue_cols[3].metric("Low Priority", low_priority)
        
        # Patient Queue Overview
        st.header("Patient Queue Overview")
        if not st.session_state.patient_queue.empty:
            st.dataframe(
                st.session_state.patient_queue.style.apply(
                    lambda x: ['background-color: #ffcccc' if x['Priority'] == 'High'
                             else 'background-color: #ffffcc' if x['Priority'] == 'Medium'
                             else 'background-color: #ccffcc' for _ in x],
                    axis=1
                )
            )
            
        
         # Approved Patients Management
        st.header("Approved Patients Management")
        if not st.session_state.approved_patients.empty:
            st.dataframe(st.session_state.approved_patients)
            
            with st.form("complete_xray"):
                st.write("Mark X-Ray Complete")
                patient_ids = st.session_state.approved_patients[
                    st.session_state.approved_patients['Status'] == 'In Progress'
                ]['Patient ID'].tolist()
                
                if patient_ids:
                    complete_patient_id = st.selectbox(
                        "Select Patient",
                        options=patient_ids
                    )
                    
                    if st.form_submit_button("Mark Complete"):
                        # Update patient status
                        patient_idx = st.session_state.approved_patients[
                            st.session_state.approved_patients['Patient ID'] == complete_patient_id
                        ].index[0]
                        
                        # Get machine ID
                        machine_id = st.session_state.approved_patients.at[patient_idx, 'Machine ID']
                        
                        # Update machine status
                        machine_idx = st.session_state.xray_machines[
                            st.session_state.xray_machines['Machine ID'] == machine_id
                        ].index[0]
                        
                        st.session_state.xray_machines.at[machine_idx, 'Status'] = 'Available'
                        st.session_state.xray_machines.at[machine_idx, 'Assigned Patient'] = 'None'
                        st.session_state.xray_machines.at[machine_idx, 'Expected Available Time'] = datetime.now()
                        
                        # Update approved patients
                        st.session_state.approved_patients.at[patient_idx, 'Status'] = 'Completed'
                        
                        st.success(f"Patient {complete_patient_id} X-ray marked as complete")
                        st.rerun()
                else:
                    st.info("No patients currently in progress")
        else:
            st.info("No approved patients")
        
        # Next Patient Selection
        st.header("Next Patient Selection")
        if not st.session_state.patient_queue.empty:
            next_patient = st.session_state.patient_queue.iloc[0]
            st.write(f"Next patient in queue: {next_patient['Name']} (Priority: {next_patient['Priority']})")
            
            available_machines = st.session_state.xray_machines[
                st.session_state.xray_machines['Status'] == 'Available'
            ]
            
            if not available_machines.empty:
                if st.button("Approve Next Patient"):
                    if allocate_xray_machine(
                        next_patient['Patient ID'],
                        next_patient['Name'],
                        next_patient['Priority']
                    ):
                        # Remove from queue
                        st.session_state.patient_queue = st.session_state.patient_queue.iloc[1:]
                        st.success(f"Patient {next_patient['Name']} approved and allocated to machine")
                        st.rerun()
            else:
                st.warning("No machines currently available")
        else:   
            st.info("No patients in queue")
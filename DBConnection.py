from pymongo import MongoClient
from bson.objectid import ObjectId

username = "football"
password = "iCaBCtqvJpGjfE4s"
connection_string = f"mongodb+srv://{username}:{password}@footballprediction.9kflzpo.mongodb.net/?retryWrites=true&w=majority&appName=FootballPrediction"

# Create a MongoClient
client = MongoClient(connection_string)

# Define the database
database = client["footballdb"]
users_collection = database['userdata']
feedback_collection = database['feedback']

def register_user(name, phone_no, email, INIT_CREDIT = 10):
    """Register a new user by inserting their data into the MongoDB collection."""
    
    # Check if user with the same phone number or email already exists
    if users_collection.find_one({"phone_no": phone_no}) or users_collection.find_one({"email": email}):
        return False  # User already exists
    
    # Create a new user document
    new_user = {
        "name": name,
        "phone_no": phone_no,
        "email": email,
        "credits": INIT_CREDIT,
        'address': None
    }
    
    # Insert the new user into the collection
    users_collection.insert_one(new_user)
    return True

def usercheck_with_payment(email, phone_no):
        # Check if user with the same phone number or email already exists
    if users_collection.find_one({"email": email}) or users_collection.find_one({"phone_no": phone_no}):
        return False
    else:
        return True

def register_user_with_payment(name, phone_no, email, INIT_CREDIT = 10, address = None):
    """Register a new user with payment added by inserting their data into the MongoDB collection."""
    
    # Create a new user document
    new_user = {
        "name": name,
        "phone_no": phone_no,
        "email": email,
        "credits": INIT_CREDIT,
        "address": address
    }
    # Insert the new user into the collection
    users_collection.insert_one(new_user)
    return True

def update_user_address(email, new_address):
    """
    Update the address of an existing user in the MongoDB collection.

    :param email: The email of the user whose address needs to be updated.
    :param new_address: The new address to be updated.
    :return: True if the update was successful, False otherwise.
    """
    
    # Check if the user with the given email has an address that is currently None
    user = users_collection.find_one({"email": email, "address": None})
    
    if user:
        # Find the user by email and update the address
        result = users_collection.update_one(
            {"email": email},
            {"$set": {"address": new_address}}
        )
        
        # Check if the update was successful
        if result.modified_count > 0:
            return True
    
    return False

def insert_feedback(feedback_data,st):
    """
    Insert feedback data into the MongoDB feedback collection.
    
    Parameters:
    feedback_data (dict): The feedback data to be inserted.
    
    Returns:
    bool: True if the insertion was successful, False otherwise.
    """
    try:
        feedback_collection.insert_one(feedback_data)
        return True
    except Exception as e:
        st.error(f"An error occurred while inserting feedback data: {e}")
        return False


def usercheck(email,st):
        # Check if user with the same phone number or email already exists
    if not users_collection.find_one({"email": email}):
        st.error('Email not found, Please Register Yourself.')

def referal_code_check(ref_code,st):
        # Check if user with the same phone number or email already exists
    if users_collection.find_one({"user_referral_code": ref_code}):
        return True
    else:
        st.error('Invalid Referral Code.')

def get_credits(email):
    """Get the credits for a user based on their email."""
    user = users_collection.find_one({"email": email}, {"credits": 1, "_id": 0})
    if user:
        return user["credits"]
    else:
        return None  # User not found

def get_name(email):
    """Get the credits for a user based on their email."""
    user = users_collection.find_one({"email": email}, {"name": 1, "_id": 0})
    if user:
        return user["name"]
    else:
        return None  # User not found
    
def decrement_credits(email, amount=5):
    """Decrement the credits of a user by a specified amount (default is 5)."""
    result = users_collection.update_one(
        {"email": email},
        {"$inc": {"credits": -amount}}
    )
    
    # Check if the user was found and updated
    if result.matched_count > 0:
        return True
    else:
        return False  # User not found

def ref_increment_credits(ref_code, amount=10):
    """Increment the credits of a user by a specified amount (default is 5)."""
    
    # Update the user's credits, incrementing by the specified amount
    result = users_collection.update_one(
        {"user_referral_code": ref_code},
        {"$inc": {"credits": amount}}
    )
    
    # Check if the user was found and updated
    if result.matched_count > 0:
        # Optional: Verify if the update was successful
        user = users_collection.find_one({"user_referral_code": ref_code})
        if user and user.get("credits", 0) >= amount:
            return True  # Success and credits are valid
        else:
            # In case of any issue with the updated value (optional check)
            return False  # User's credits might not be valid, but this is unlikely for increment
    else:
        return False  # User not found

def increment_credits(email, amount=5):
    """Increment the credits of a user by a specified amount (default is 5)."""
    
    # Update the user's credits, incrementing by the specified amount
    result = users_collection.update_one(
        {"email": email},
        {"$inc": {"credits": amount}}
    )
    
    # Check if the user was found and updated
    if result.matched_count > 0:
        # Optional: Verify if the update was successful
        user = users_collection.find_one({"email": email})
        if user and user.get("credits", 0) >= amount:
            return True  # Success and credits are valid
        else:
            # In case of any issue with the updated value (optional check)
            return False  # User's credits might not be valid, but this is unlikely for increment
    else:
        return False  # User not found


def get_user_data(email=None, phone=None):
    # Ensure either email or phone is provided
    if not email and not phone:
        return None  # Neither email nor phone provided

    # Build the query filter based on available identifier(s)
    query_filter = {}
    if email:
        query_filter["email"] = email
    if phone:
        query_filter["phone_no"] = phone

    # Fetch user data
    user_data = users_collection.find_one(query_filter)
    return user_data

def update_user_data(user_id, updated_data):
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": updated_data}
    )
    return result.modified_count > 0

def add_feedback_status(email, status = False):
    """
    Add a feedback submitted status column to a user's entry.
    
    Parameters:
    email (str): The email of the user whose entry will be updated.
    
    Returns:
    bool: True if the update was successful, False otherwise.
    """
    try:
        result = users_collection.update_one(
            {"email": email},
            {"$set": {"feedback_submitted": status}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"An error occurred while updating the user data: {e}")
        return False
        
def get_feedback_status(email,st):
    """
    Get the feedback submitted status of a user.
    
    Parameters:
    email (str): The email of the user whose feedback status will be retrieved.
    
    Returns:
    bool: True if feedback was submitted, False if not submitted, None if user not found.
    """
    try:
        user = users_collection.find_one({"email": email}, {"feedback_submitted": 1})
        if user:
            return user.get("feedback_submitted", None)
        return None
    except Exception as e:
        st.error(f"An error occurred while retrieving feedback status: {e}")
        return None

def set_referral_code(email, code):
    """
    Set a user's referral code if it is not already set.
    
    Parameters:
    email (str): The email of the user whose entry will be updated.
    code (str): The referral code to set for the user.
    
    Returns:
    bool: True if the update was successful, False otherwise.
    """
    try:
        user = users_collection.find_one({"email": email})
        
        if user is not None:
            if user.get("user_referral_code") is None:
                result = users_collection.update_one(
                    {"email": email},
                    {"$set": {"user_referral_code": code}}
                )
                return result.modified_count > 0
            else:
                print("Referral code already set.")
                return False
        else:
            print("User not found.")
            return False
    except Exception as e:
        print(f"An error occurred while updating the user data: {e}")
        return False

def set_referral(email, ref_code):
    try:
        result = users_collection.update_one(
            {"email": email},
            {"$set": {"client_referral": ref_code}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"An error occurred while updating the user data: {e}")
        return False
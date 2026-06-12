"""
Tests for activity endpoints: GET /activities, POST /signup, POST /remove.
Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivitiesEndpoint:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: TestClient is available via fixture with reset activities.
        Act: Request all activities.
        Assert: Verify response includes all activities with correct structure.
        """
        # Act: Call GET /activities
        response = client.get("/activities")
        
        # Assert: Check status code
        assert response.status_code == 200, "Should return 200 OK"
        
        # Assert: Verify response is JSON
        activities = response.json()
        assert isinstance(activities, dict), "Response should be a dictionary"
        
        # Assert: Verify expected activities are present
        assert "Chess Club" in activities, "Chess Club should be in activities"
        assert "Programming Class" in activities, "Programming Class should be in activities"
        assert "Gym Class" in activities, "Gym Class should be in activities"
    
    def test_activity_structure(self, client):
        """
        Arrange: TestClient is available via fixture.
        Act: Fetch activities and check one activity's structure.
        Assert: Verify each activity has required fields.
        """
        # Act: Get all activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Check structure of one activity
        activity = activities["Chess Club"]
        assert "description" in activity, "Activity should have description"
        assert "schedule" in activity, "Activity should have schedule"
        assert "max_participants" in activity, "Activity should have max_participants"
        assert "participants" in activity, "Activity should have participants list"
        assert isinstance(activity["participants"], list), "Participants should be a list"
    
    def test_get_activities_has_correct_participant_count(self, client):
        """
        Arrange: TestClient with reset activities (Chess Club has 2 participants).
        Act: Get activities.
        Assert: Verify participant counts match expected values.
        """
        # Act: Get all activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Check participant counts
        assert len(activities["Chess Club"]["participants"]) == 2, \
            "Chess Club should have 2 initial participants"
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"], \
            "michael should be in Chess Club"
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"], \
            "daniel should be in Chess Club"


class TestSignupEndpoint:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client, activity_with_spots, sample_email):
        """
        Arrange: Prepare valid activity name and unique email.
        Act: Sign up a student for an activity.
        Assert: Verify signup succeeds and participant is added.
        """
        # Act: Sign up for an activity
        response = client.post(
            f"/activities/{activity_with_spots}/signup",
            params={"email": sample_email}
        )
        
        # Assert: Check response status
        assert response.status_code == 200, "Signup should succeed (200 OK)"
        
        # Assert: Check response message
        result = response.json()
        assert "message" in result, "Response should contain a message"
        assert sample_email in result["message"], "Message should mention the email"
        
        # Assert: Verify participant was added
        verify = client.get("/activities")
        activities = verify.json()
        assert sample_email in activities[activity_with_spots]["participants"], \
            "Student should be in participants list"
    
    def test_signup_activity_not_found(self, client, sample_email):
        """
        Arrange: Use a non-existent activity name.
        Act: Try to sign up for non-existent activity.
        Assert: Verify 404 error is returned.
        """
        # Act: Try to sign up for activity that doesn't exist
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": sample_email}
        )
        
        # Assert: Check error status
        assert response.status_code == 404, "Should return 404 Not Found"
        
        # Assert: Check error message
        error = response.json()
        assert "detail" in error, "Error response should have detail"
        assert "Activity not found" in error["detail"], \
            "Error message should mention activity not found"
    
    def test_signup_duplicate_student(self, client, activity_with_spots):
        """
        Arrange: Use a student already signed up for the activity.
        Act: Try to sign up the same student again.
        Assert: Verify 400 Bad Request error is returned.
        """
        # Arrange: Get an existing participant from Programming Class
        existing_email = "emma@mergington.edu"  # Already in Programming Class
        
        # Act: Try to sign up again
        response = client.post(
            f"/activities/{activity_with_spots}/signup",
            params={"email": existing_email}
        )
        
        # Assert: Check error status
        assert response.status_code == 400, "Should return 400 Bad Request"
        
        # Assert: Check error message
        error = response.json()
        assert "detail" in error, "Error response should have detail"
        assert "already signed up" in error["detail"], \
            "Error message should mention duplicate signup"
    
    def test_signup_multiple_students_different_activities(self, client, sample_email):
        """
        Arrange: Prepare two different activities.
        Act: Sign up same student for different activities.
        Assert: Verify student appears in both activities' participant lists.
        """
        # Act: Sign up for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )
        
        # Assert: First signup succeeds
        assert response1.status_code == 200, "First signup should succeed"
        
        # Act: Sign up for second activity
        response2 = client.post(
            "/activities/Gym Class/signup",
            params={"email": sample_email}
        )
        
        # Assert: Second signup succeeds
        assert response2.status_code == 200, "Second signup should succeed"
        
        # Assert: Verify student in both activities
        verify = client.get("/activities")
        activities = verify.json()
        assert sample_email in activities["Chess Club"]["participants"], \
            "Student should be in Chess Club"
        assert sample_email in activities["Gym Class"]["participants"], \
            "Student should be in Gym Class"


class TestRemoveEndpoint:
    """Test suite for POST /activities/{activity_name}/remove endpoint"""
    
    def test_successful_remove(self, client, activity_with_spots):
        """
        Arrange: Prepare an activity with known participants.
        Act: Remove a participant from the activity.
        Assert: Verify participant is removed from the list.
        """
        # Arrange: Get initial participant
        verify_before = client.get("/activities")
        activities_before = verify_before.json()
        initial_count = len(activities_before[activity_with_spots]["participants"])
        email_to_remove = activities_before[activity_with_spots]["participants"][0]
        
        # Act: Remove the participant
        response = client.post(
            f"/activities/{activity_with_spots}/remove",
            params={"email": email_to_remove}
        )
        
        # Assert: Check response status
        assert response.status_code == 200, "Remove should succeed (200 OK)"
        
        # Assert: Check response message
        result = response.json()
        assert "message" in result, "Response should contain a message"
        assert "Removed" in result["message"], "Message should mention removal"
        
        # Assert: Verify participant was removed
        verify_after = client.get("/activities")
        activities_after = verify_after.json()
        new_count = len(activities_after[activity_with_spots]["participants"])
        assert new_count == initial_count - 1, "Participant count should decrease by 1"
        assert email_to_remove not in activities_after[activity_with_spots]["participants"], \
            "Removed participant should no longer be in list"
    
    def test_remove_activity_not_found(self, client):
        """
        Arrange: Use a non-existent activity name.
        Act: Try to remove from non-existent activity.
        Assert: Verify 404 error is returned.
        """
        # Act: Try to remove from activity that doesn't exist
        response = client.post(
            "/activities/Nonexistent Activity/remove",
            params={"email": "test@mergington.edu"}
        )
        
        # Assert: Check error status
        assert response.status_code == 404, "Should return 404 Not Found"
        
        # Assert: Check error message
        error = response.json()
        assert "detail" in error, "Error response should have detail"
        assert "Activity not found" in error["detail"], \
            "Error message should mention activity not found"
    
    def test_remove_participant_not_in_activity(self, client, activity_with_spots):
        """
        Arrange: Use a valid activity and an email not in that activity's participants.
        Act: Try to remove a participant who isn't in the activity.
        Assert: Verify 404 error is returned.
        """
        # Arrange: Use an email that's not in Programming Class
        email_not_in_activity = "notpresent@mergington.edu"
        
        # Act: Try to remove non-existent participant
        response = client.post(
            f"/activities/{activity_with_spots}/remove",
            params={"email": email_not_in_activity}
        )
        
        # Assert: Check error status
        assert response.status_code == 404, "Should return 404 Not Found"
        
        # Assert: Check error message
        error = response.json()
        assert "detail" in error, "Error response should have detail"
        assert "not found" in error["detail"].lower(), \
            "Error message should mention student not found"
    
    def test_remove_then_signup_same_student(self, client, activity_with_spots):
        """
        Arrange: Remove a student from an activity.
        Act: Sign up the same student again.
        Assert: Verify student can be re-added to the activity.
        """
        # Arrange: Get an existing participant
        verify_before = client.get("/activities")
        activities_before = verify_before.json()
        email = activities_before[activity_with_spots]["participants"][0]
        
        # Act: Remove the participant
        remove_response = client.post(
            f"/activities/{activity_with_spots}/remove",
            params={"email": email}
        )
        assert remove_response.status_code == 200, "Remove should succeed"
        
        # Act: Sign up again
        signup_response = client.post(
            f"/activities/{activity_with_spots}/signup",
            params={"email": email}
        )
        
        # Assert: Re-signup should succeed
        assert signup_response.status_code == 200, "Re-signup should succeed"
        
        # Assert: Verify participant is back in list
        verify_after = client.get("/activities")
        activities_after = verify_after.json()
        assert email in activities_after[activity_with_spots]["participants"], \
            "Student should be back in participants list"

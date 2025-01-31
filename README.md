# Rizzder Web Server

## Application Overview
Rizzder is a Tinder-like web application where users can meet, chat, and share photos. Each user manages their account, including:
- Updating personal descriptions and dating preferences.
- Uploading and deleting photos.
- Setting a profile picture.
- Matching with compatible users and initiating text conversations.
- Respectfully unmatching users if needed.
- Avoiding ghosting and unjustified blocking, which can result in **penalties**.

---
## Application Flow
1. **Home Page:** Users are greeted and encouraged to sign up based on positive past experiences.
2. **Signup Process:**
   - Users create an account by providing a username, a strong password, and their birthdate.
3. **Profile Management:**
   - Users can edit their profile, update preferences, and upload photos via the profile icon in the top-right corner.
4. **Matching System:**
   - Users can browse compatible profiles by clicking the matching icon.
   - They can choose to **smash** (like) or **pass** (dislike) users.
   - If both users like each other, a chat is enabled.
5. **Chat System:**
   - Users can access active chats via the chat icon in the navigation bar.
6. **Support & Info:**
   - Clicking the info icon provides access to an "About Us" page with contact details, a FAQ section, and location details.

---
## Technologies Used
- **Backend:** Python with Django (requires Python 3.13.1).
- **Frontend:** HTML, CSS, JavaScript.
- **Database:** SQLite (tracks user location for penalties, not other purposes).
- **Authentication:** JWT-based authentication (tokens stored in cookies).
- **Security:** HTTPS is enforced for user safety.
- **Hosting & Deployment:** Render (provides free benefits and **does not require a credit card**).
- **Development Tools:**
  - Primary IDE: PyCharm.
  - Secondary: GitHub’s integrated editor.
  - Filtering algorithms using SQL subqueries and joins for matchmaking.

---
## Individual Contributions
- **Backend Infrastructure:** Cazacu Alexandru-Dan
- **UI/UX Design:** Plopeanu Teodora-Anca
- **Home & Profile Pages:** Plopeanu Teodora-Anca
- **Navigation Bar:** Plopeanu Teodora-Anca
- **Chat System:** Ungureanu Vlad-Marin
- **Matching System:** Ungureanu Vlad-Marin
- **About Us Page:** Giurgiu Andrei-Ștefan
- **Deployment & Hosting:** Giurgiu Andrei-Ștefan

---
## Challenges & Solutions
### Deployment Issues
- **Static Files Not Loading:**
  - Django does not collect static files by default.
  - Solution: Created a designated folder for static files and added the following command in the Procfile:
    ```sh
    python3 manage.py collectstatic --noinput
    ```

### Development & Debugging Challenges
- **Module Compatibility:**
  - Switching between computers required reinstalling modules.
  - Solution: Created a `requirements.txt` file listing all dependencies.
- **Database Migration Issues:**
  - Migrating between systems required reapplying migrations.

### Frontend Challenges
- **Scrollbar Issues:**
  - Some HTML pages failed to display scrollbars correctly.
  - Solution: Added `overflow: auto;` to CSS styles.

### PyCharm Frustrations
- **Slow Startup:**
  - One team member experienced 10-minute startup times.
  - No solution found; frustration evident in commit messages (e.g., **"I hate PyCharm"**).

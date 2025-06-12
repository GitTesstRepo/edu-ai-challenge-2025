# Title
Logout Button Not Working on Safari

## Description
The Logout button does not respond when clicked in the Safari browser. No error message is shown, and the user remains logged in without any indication of a failed operation. This issue is not reproducible in other browsers such as Chrome or Firefox.

## Steps to Reproduce
1. Open the application in Safari browser.
2. Log into a valid user account.
3. Attempt to click the "Logout" button located in the navigation/header.
4. Observe that no action is taken.

## Expected vs Actual Behavior
**Expected:**  
Upon clicking the "Logout" button, the user should be logged out and redirected to the login page (or landing page depending on application design).

**Actual:**  
Nothing happens when the Logout button is clicked. The user remains on the same page and stays logged in. There is no visible error or response.

## Environment
- Browser: Safari (version: `{{INSERT VERSION HERE}}`)
- Operating System: `{{INSERT OS NAME AND VERSION}}`
- Application Version: `{{INSERT APP VERSION HERE}}`
- Device: `{{INSERT DEVICE MODEL IF APPLICABLE}}`

## Severity or Impact
**Severity:** Medium  
**Impact:** Affects all Safari users; prevents logout functionality, which is a critical security and user experience issue.

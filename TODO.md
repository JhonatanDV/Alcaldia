# Role-Based Access Control Implementation

## Backend Changes
- [ ] Modify UserCreateSerializer to include 'role' field for group assignment
- [ ] Update UserInfoView to return user groups
- [ ] Run management command to create initial roles

## Frontend Changes
- [ ] Update LoginForm to determine role based on groups ('Administrador' = admin, else technician)
- [ ] Update dashboard page to show different UI based on user role

## Testing
- [ ] Test user creation with role assignment
- [ ] Test login and role determination
- [ ] Implement role-specific UI features

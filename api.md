## API

### Iteration 1:

| type & name         | arg <br> [arg] - additional     | result |
|:-------------|:----------|:-----------|
| mutate login |  email <br> password | ok <br> user |
| mutate validateName | firstName <br> lastName | ok <br> errorInfo |
| mutate validateBirthdate | birthdate | ok <br> errorInfo |
| mutate validateJob | jobTitle | ok <br> errorInfo |
| mutate validateCompany | company | ok <br> errorInfo |
| mutate validateEmail | email | ok <br> errorInfo |
| mutate validatePassword | password <br> repeatedPassword | ok <br> errorInfo |
| mutate registration | firstName <br> lastName <br> birthdate <br> jobTitle <br> company <br> email <br> password <br> repeatedPassword | ok <br> errorInfo <br> user |
| mutate userUpdate | sessionKey <br> [firstName] <br> [lastName] <br> [birthdate] <br> [jobTitle] <br> [company] <br> [email] <br> [password] | ok <br> errorInfo <br> user |
| mutate addTask | sessionKey <br> name <br> executionDate <br> [deadline] <br> [description] <br> [fruits] <br> [usersId] <br> [groupId] | ok <br> errorInfo <br> task |
| mutate updateTask | sessionKey <br> taskId <br> [name] <br> [executionDate] <br> [deadline] <br> [description] <br> [fruits] <br> [state] | ok <br> errorInfo <br> task |
| mutate changePriorityTask | sessionKey <br> taskId <br> [previousTaskId] <br> [personalDate] | ok <br> errorInfo <br> tasks |
| query userTasks | sessionKey | userTasks |

### Iteration 2:

| type & name         | arg <br> [arg] - additional     | result |
|:-------------|:----------|:-----------|
| query users | sessionKey <br> [id] <br> [firstName] <br> [lastName] <br> [email] <br> [birthdate] <br> [jobTitle] <br> [company] <br> [sessionKey] | users |
| query otherUserTasks | sessionKey <br> otherId | otherUserTasks |
| query pingList | sessionKey | pingList |
| query pingDataForRequest | sessionKey <br> taskId | pingDataForRequest |
| query pingDataForAnswer | sessionKey <br> pingId | pingDataForAnswer |
| mutation sendPing | sessionKey <br> otherId <br> taskId <br> pingType <br> message | ok <br> errorInfo |
| mutation setPingEnded | sessionKey <br> pingId | ok <br> errorInfo |

### Iteration 3:

| type & name         | arg <br> [arg] - additional     | result |
|:-------------|:----------|:-----------|
| mutation addGroup | sessionKey <br> name <br> [description] | ok <br> errorInfo <br> group |
| mutation addGroupMember | sessionKey <br> groupId <br> userId | ok <br> errorInfo |
| mutation leaveGroup | sessionKey <br> groupId | ok <br> errorInfo |
| mutation deleteGroupMember | sessionKey <br> groupId <br> userId | ok <br> errorInfo |
| mutation shareTask | sessionKey <br> taskId <br> [groupId] <br> [userId] | ok <br> errorInfo |
| query commonUserTasks | sessionKey <br> otherId | tasks |
| query groups | [id] <br> [name] | groups |
| query userGroups | sessionKey | groups |

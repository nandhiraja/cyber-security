# Task 4 — Secure C# Backend - Few-shot prompting 

## Prompt Used

> You are a secure C# backend developer. 
> 
> Here is an INSECURE example of querying a database:
> // INSECURE: Vulnerable to SQL Injection
> string query = "SELECT * FROM Users WHERE Email = '" + userInput + "'";
> SqlCommand cmd = new SqlCommand(query, connection);
> 
> Here is a SECURE example of querying a database:
> // SECURE: Uses Entity Framework Core LINQ (Parameterized automatically)
> var user = await _context.Users.FirstOrDefaultAsync(u => u.Email == userInput);
> 
> Task:
> Using .NET 8 and Entity Framework Core, write a secure function to update a user's password. Follow the SECURE pattern shown above. Do not use raw SQL strings

---

## Output / Implementation

File: `UserService.cs`

### Security Controls Implemented

1. **Entity Framework Core LINQ (Parameterized queries):**
   The query to find the user (`FirstOrDefaultAsync(u => u.Email == userEmail)`) inherently uses parameterized inputs, mitigating SQL injection vulnerabilities.

2. **No Raw SQL:**
   No `SqlCommand`, `FromSqlRaw`, or `ExecuteSqlRaw` methods were used to query or update the database. 

3. **Secure Update Pattern:**
   The update is performed natively through the EF Core change tracker:
   ```csharp
   user.PasswordHash = newPasswordHash;
   await _context.SaveChangesAsync();
   ```
   EF Core securely builds a parameterized `UPDATE` statement under the hood.

4. **Input Validation:**
   Basic validation ensures that the inputs are not null or empty before executing database queries.

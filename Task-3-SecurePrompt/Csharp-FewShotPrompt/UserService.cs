using System;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;

namespace SecureApp.Services
{
    public class UserService
    {
        private readonly AppDbContext _context;

        public UserService(AppDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Updates a user's password securely using Entity Framework Core.
        /// </summary>
        /// <param name="userEmail">The email of the user.</param>
        /// <param name="newPasswordHash">The hashed new password.</param>
        /// <returns>True if the update was successful, otherwise false.</returns>
        public async Task<bool> UpdateUserPasswordAsync(string userEmail, string newPasswordHash)
        {
            if (string.IsNullOrWhiteSpace(userEmail) || string.IsNullOrWhiteSpace(newPasswordHash))
            {
                throw new ArgumentException("Email and password hash cannot be empty.");
            }

            var user = await _context.Users.FirstOrDefaultAsync(u => u.Email == userEmail);

            if (user == null)
            {
                return false;
            }

            user.PasswordHash = newPasswordHash;
            await _context.SaveChangesAsync();

            return true;
        }
    }

    public class AppDbContext : DbContext
    {
        public DbSet<User> Users { get; set; }
    }

    public class User
    {
        public int Id { get; set; }
        public string Email { get; set; }
        public string PasswordHash { get; set; }
    }
}

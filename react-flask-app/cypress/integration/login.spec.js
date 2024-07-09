// cypress/integration/login.spec.js
describe('Login Page Tests', () => {
    beforeEach(() => {
      cy.visit('http://forteam22ict.xyz/login') 
    })
  
    it('should display the login form', () => {
      cy.get('form').should('be.visible')
    })
  
    it('should show OTP input field for valid credentials', () => {
      cy.get('input[name="email"]').type('2201906@sit.singaporetech.edu.sg') // Use a test email
      cy.get('input[name="password"]').type('Password123!') // Use a test password
      cy.get('button[type="submit"]').click()
  
      // Assert the OTP input field is displayed
      cy.get('input[name="otp"]').should('be.visible')
    })
  
    it('should show an error message for invalid OTP', () => {
      cy.get('input[name="email"]').type('2201906@sit.singaporetech.edu.sg') // Use a test email
      cy.get('input[name="password"]').type('Password123!') // Use a test password
      cy.get('button[type="submit"]').click()
  
      // Enter invalid OTP and submit
      cy.get('input[name="otp"]').type('123456')
      cy.get('button[type="submit"]').click()
  
      // Assert an error message is displayed
      cy.get('.error').should('be.visible') // Adjust the selector if needed
    })
  
    it('should show an error message for invalid credentials', () => {
      cy.get('input[name="email"]').type('invalid@example.com')
      cy.get('input[name="password"]').type('invalidpassword')
      cy.get('button[type="submit"]').click()
  
      cy.get('.error').should('be.visible') // Adjust the selector if needed
    })
  })
  
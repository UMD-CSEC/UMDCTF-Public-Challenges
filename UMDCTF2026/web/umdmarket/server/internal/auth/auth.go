package auth

import (
	"errors"
	"fmt"
	"sync"
	"unicode"

	"golang.org/x/crypto/bcrypt"
)

var (
	ErrUsernameTaken      = errors.New("username taken")
	ErrInvalidCredentials = errors.New("invalid credentials")
	ErrWeakPassword       = errors.New("weak password")
	ErrInvalidUsername     = errors.New("invalid username")
)

const StartingBalance uint64 = 1_000_000 // $100.00 in price units

// Position tracks YES/NO contract quantities for a ticker.
type Position struct {
	YesQty uint32
	NoQty  uint32
}

// User represents a registered user.
type User struct {
	Username     string
	PasswordHash []byte
	Balance      uint64
	Positions    map[uint16]*Position
}

// UserStore is a thread-safe in-memory user database.
type UserStore struct {
	mu    sync.RWMutex
	users map[string]*User
}

// NewUserStore creates an empty user store.
func NewUserStore() *UserStore {
	return &UserStore{
		users: make(map[string]*User),
	}
}

// Register creates a new user account.
func (s *UserStore) Register(username, password string) (*User, error) {
	if err := validateUsername(username); err != nil {
		return nil, err
	}
	if err := validatePassword(password); err != nil {
		return nil, err
	}

	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, fmt.Errorf("bcrypt: %w", err)
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.users[username]; exists {
		return nil, ErrUsernameTaken
	}

	user := &User{
		Username:     username,
		PasswordHash: hash,
		Balance:      StartingBalance,
		Positions:    make(map[uint16]*Position),
	}
	s.users[username] = user
	return user, nil
}

// Login validates credentials and returns the user.
func (s *UserStore) Login(username, password string) (*User, error) {
	s.mu.RLock()
	user, exists := s.users[username]
	s.mu.RUnlock()

	if !exists {
		return nil, ErrInvalidCredentials
	}

	if err := bcrypt.CompareHashAndPassword(user.PasswordHash, []byte(password)); err != nil {
		return nil, ErrInvalidCredentials
	}

	return user, nil
}

// GetUser returns a user by username (nil if not found).
func (s *UserStore) GetUser(username string) *User {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.users[username]
}

func validateUsername(username string) error {
	if len(username) < 8 {
		return fmt.Errorf("%w: must be at least 8 characters", ErrInvalidUsername)
	}
	for _, r := range username {
		if !unicode.IsLetter(r) && !unicode.IsDigit(r) {
			return fmt.Errorf("%w: alphanumeric only", ErrInvalidUsername)
		}
	}
	return nil
}

func validatePassword(password string) error {
	if len(password) < 12 {
		return fmt.Errorf("%w: must be at least 12 characters", ErrWeakPassword)
	}
	var hasUpper, hasLower, hasDigit, hasSpecial bool
	for _, r := range password {
		switch {
		case unicode.IsUpper(r):
			hasUpper = true
		case unicode.IsLower(r):
			hasLower = true
		case unicode.IsDigit(r):
			hasDigit = true
		default:
			hasSpecial = true
		}
	}
	if !hasUpper || !hasLower || !hasDigit || !hasSpecial {
		return fmt.Errorf("%w: must contain uppercase, lowercase, digit, and special character", ErrWeakPassword)
	}
	return nil
}

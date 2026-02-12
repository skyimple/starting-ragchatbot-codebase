# Frontend Changes - Dark/Light Theme Toggle

## Summary
Added a dark/light theme toggle button that allows users to switch between dark and light color schemes. The toggle is positioned in the top-right corner, uses sun/moon icons with smooth animations, and persists the user's preference in localStorage.

## Changes Made

### 1. `frontend/index.html`
- **Added theme toggle button** with sun and moon SVG icons
- Button positioned fixed in top-right corner
- Includes proper ARIA labels for accessibility
- Updated version numbers for CSS (v=10) and JS (v=10) to ensure cache refresh

### 2. `frontend/style.css`
- **Added light theme CSS variables** under `:root[data-theme="light"]`
  - Light backgrounds (#ffffff, #f8fafc)
  - Dark text colors (#1e293b, #64748b)
  - Adjusted shadows and border colors for light theme

- **Added theme toggle button styles**:
  - Fixed positioning (top: 1rem, right: 1rem)
  - Circular design (44px diameter)
  - Hover and active states with scale animations
  - Focus ring for keyboard accessibility
  - Icon rotation and opacity transitions

- **Added smooth theme transitions** for all major elements:
  - body, container, sidebar, chat container
  - Messages, inputs, buttons
  - All transitions use 0.3s ease timing

- **Added light theme specific adjustments**:
  - Scrollbar styling for light theme
  - Code block background adjustments
  - Error/success message color adjustments

### 3. `frontend/script.js`
- **Added theme management functions**:
  - `initTheme()` - Loads saved theme from localStorage or defaults to dark
  - `setTheme(theme)` - Sets the data-theme attribute and saves preference
  - `toggleTheme()` - Switches between dark and light themes

- **Added theme toggle event listeners**:
  - Click handler on theme toggle button
  - Keyboard support (Enter and Space keys)
  - Proper event prevention for keyboard interactions

## Features

### Design
- Icon-based toggle button with sun (light) and moon (dark) icons
- Smooth rotation and scale animations when switching themes
- Positioned in top-right corner with 44px touch target size

### Accessibility
- ARIA labels for screen readers ("Toggle theme")
- Title attribute for tooltip on hover
- Keyboard navigable with Enter and Space keys
- Focus ring for visible keyboard focus

### User Experience
- Theme preference persists in localStorage across sessions
- 0.3s smooth transitions for all color changes
- Hover and active states for visual feedback
- Default dark theme matches existing design

## CSS Variables

### Dark Theme (Default)
```css
--background: #0f172a
--surface: #1e293b
--text-primary: #f1f5f9
--text-secondary: #94a3b8
```

### Light Theme
```css
--background: #ffffff
--surface: #f8fafc
--text-primary: #1e293b
--text-secondary: #64748b
```

## Browser Compatibility
- Modern browsers with CSS variable support
- localStorage API for theme persistence
- CSS transitions and transforms for animations

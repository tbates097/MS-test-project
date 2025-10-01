# Aerotech UI Guidelines

This document outlines the design system and UI guidelines for Aerotech applications, including typography, color schemes, and iconography specifications.

## Table of Contents

- [Typography](#typography)
- [Color System](#color-system)
- [Iconography](#iconography)

---

## Typography

### Font Family
- **Primary Font**: Source Sans Pro
- **Available Styles**: Semibold, Semibold Italic, Regular, Italic
- **Units**: Microsoft WPF's default unit, Device-Independent Pixels (DIP)

### Text Styles

| Style | Font | Line Spacing | Size | Usage |
|-------|------|--------------|------|-------|
| H1 Headline | Source Sans Pro Semibold | 25 | 20 | Application Toolbar Title, Dialog Window Title, Machine Setup |
| H2 Headline | Source Sans Pro Semibold | 24 | 18 | Section headers |
| T1 Text | Source Sans Pro Semibold | 24 | 16 | Message Bar, Machine Setup instructional header |
| T2 Text | Source Sans Pro Regular | 24 | 16 | Text Input, Segmented Button Selection, Button Text, Tabs, List, Checkbox text, Radio button text |
| T3 List | Source Sans Pro Regular | 26 | 16 | Menus, List Links Default, Dialog Box |

### Programming Font
- **Typeface**: Monospace 821 BT, Roman
- **Size**: 16 DP

### Color Usage in Typography

#### H1 Headline
- **White**: Application Toolbar Title
- **Grey 1**: Dialog Window Title, Machine Setup

#### T1 Text
- **White**: Message Bar
- **Grey 3**: General text
- **Blue 1 Italic**: Files/sections with unsaved changes
- **Grey 1**: Machine Setup instructional header

#### T2 Text
- **Black**: Text Input, Segmented Button Selection
- **Blue 1**: List Link Default
- **Grey 1**: Button Text, Tabs, List, Checkbox text, Radio button text
- **White**: List Selection, Dialog Box text
- **Blue 1 Hover**: Link Hover
- **Grey 3**: Link Disabled, Subtext

#### T3 Text
- **Grey 1**: Menus, List Links Default, Dialog Box, Segmented Button Selection
- **Blue 1 Italic**: Certain text in menus
- **Grey 3**: List Links Disabled

---

## Color System

### Primary Colors

| Color | Name | Hex Code | RGB | Pantone |
|-------|------|----------|-----|---------|
| Blue 1 | Primary Blue | `#0082BE` | `rgb(0, 130, 190)` | Pantone Process Blue C |
| Grey 1 | Primary Grey | `#4B545E` | `rgb(75, 84, 94)` | Pantone 431 C |
| Grey 2 | Light Grey | `#DAE1E9` | `rgb(218, 225, 233)` | Pantone 649 C |

### Secondary Colors

| Color | Name | Hex Code | RGB |
|-------|------|----------|-----|
| Black | Primary Black | `#231F20` | `rgb(35, 31, 32)` |
| Grey 3 | Medium Grey | `#B5BBC3` | `rgb(181, 187, 195)` |
| Grey 4 | Light Medium Grey | `#C2C8CF` | `rgb(194, 200, 207)` |
| Grey 5 | Very Light Grey | `#ECEFF3` | `rgb(236, 239, 243)` |
| Grey 6 | Background Grey | `#F7F8F8` | `rgb(247, 248, 248)` |
| Red 1 | Error Red | `#DB2115` | `rgb(219, 33, 21)` |
| Orange 1 | Warning Orange | `#EF8B22` | `rgb(235, 140, 35)` |
| Yellow 1 | Axis Manager Yellow | `#FFDA00` | `rgb(255, 218, 0)` |
| Green 1 | Success Green | `#459A34` | `rgb(69, 154, 52)` |
| Yellow 2 | Text Highlight | `#FFF800` | `rgb(255, 248, 0)` |

### Hover States
*All hover states are 15% lighter than the original color*

| Color | Hover Hex | Hover RGB |
|-------|-----------|-----------|
| Blue 1 | `#1C94D2` | `rgb(28, 148, 210)` |
| Grey 1 | `#7B868C` | `rgb(123, 134, 140)` |
| Grey 2 | `#E0E5EC` | `rgb(224, 229, 236)` |
| Black | `#231F20` | `rgb(35, 31, 32)` |
| Grey 3 | `#B5BBC3` | `rgb(181, 187, 195)` |
| Red 1 | `#F15B44` | `rgb(241, 91, 68)` |
| Orange 1 | `#FAAC58` | `rgb(250, 172, 88)` |
| Yellow 1 | `#FFE432` | `rgb(255, 228, 50)` |
| Green 1 | `#68B05B` | `rgb(104, 176, 91)` |

### Color Usage Guidelines

| Color | Usage |
|-------|-------|
| **Blue 1** | Primary buttons, Module icons |
| **Grey 1** | Text color, Sidebar icons, Workspace Toolbar icons, Application Toolbar |
| **Grey 2** | Disabled elements, Application Toolbar icons, Selected tabs |
| **Black** | Text fields |
| **Grey 3** | Module titles, Disabled text, Disabled axis |
| **Grey 5** | Module headers |
| **Grey 6** | Table row alternates, Scroll bars |
| **Red 1** | Errors |
| **Orange 1** | Warnings, Abort, Paused |
| **Yellow 1** | Axis Manager |
| **Green 1** | Success status, Enabled/Active |
| **Yellow 2** | Text Highlight |

### Programming Colors
*For text in Programming module and visual graphs*

#### Group 1 (Recommended for fewer than 6 colors, common color vision deficiencies)

| Color | Hex | RGB |
|-------|-----|-----|
| P1 | `#F6921E` | `rgb(246, 146, 30)` |
| P4 | `#DD3B94` | `rgb(221, 59, 148)` |
| P6 | `#7A2A89` | `rgb(122, 42, 137)` |
| P8 | `#1E8AC1` | `rgb(30, 138, 193)` |
| P10 | `#199E49` | `rgb(25, 158, 73)` |

#### Group 2

| Color | Hex | RGB |
|-------|-----|-----|
| P2 | `#F05A28` | `rgb(240, 90, 40)` |
| P3 | `#CE2027` | `rgb(205, 32, 39)` |
| P11 | `#9A8479` | `rgb(154, 132, 121)` |
| P12 | `#754C28` | `rgb(117, 76, 40)` |
| P5 | `#A74C9B` | `rgb(167, 76, 155)` |
| P7 | `#3A4EA1` | `rgb(58, 78, 161)` |
| P9 | `#1C847D` | `rgb(28, 132, 125)` |

---

## Iconography

### General Specifications

- **Bounding Box (Maximum size)**: 14×12 pixels
- **Spacing between icons**: 7.25mm
- **Spacing between Icons with Option**: 9.5mm

### Touch Interface Icons

- **Minimum Size**: 13×13mm

---

## Implementation Notes

- All measurements are in Device-Independent Pixels (DIP) unless otherwise specified
- Hover states are automatically calculated as 15% lighter than the base color
- Programming colors should be used in order of preference (Group 1 first, then Group 2)
- Ensure proper contrast ratios for accessibility compliance
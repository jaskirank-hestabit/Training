# UI Component Library

## Button

Props:
- variant: primary | secondary | outline | danger
- size: sm | md | lg

Usage:
<Button variant="primary">Click Me</Button>

---

## Input

Props:
- label
- type
- ...rest

Usage:
<Input label="Email" placeholder="Enter email" />

---

## Card

Usage:
<Card>
  Content here
</Card>

---

## Badge

Props:
- variant: success | warning | error | info

Usage:
<Badge variant="success">Active</Badge>

---

## Modal

Props:
- isOpen
- onClose

Usage:
<Modal isOpen={open} onClose={() => setOpen(false)}>
  Modal Content
</Modal>

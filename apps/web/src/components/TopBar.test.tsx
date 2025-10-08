import { describe, it, expect } from 'vitest';
import { render, screen } from '../test/utils';
import { TopBar } from './TopBar';

describe('TopBar', () => {
  it('renders application title', () => {
    render(<TopBar />);

    expect(screen.getByText(/cxygpt/i)).toBeInTheDocument();
  });

  it('renders menu button', () => {
    render(<TopBar />);

    // Button has Chinese title "切换侧边栏"
    const button = screen.getByRole('button', { name: /切换侧边栏/i });
    expect(button).toBeInTheDocument();
  });

  it('renders settings button', () => {
    render(<TopBar />);

    // Button has Chinese title "设置"
    const button = screen.getByRole('button', { name: /设置/i });
    expect(button).toBeInTheDocument();
  });
});

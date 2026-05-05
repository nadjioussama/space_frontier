import React from "react";
import { render, screen } from "@testing-library/react";
import { AnimatedCard } from "@/components/AnimatedCard";


describe("AnimatedCard", () => {
  it("renders children", () => {
    render(
      <AnimatedCard>
        <span>Card content</span>
      </AnimatedCard>
    );

    expect(screen.getByText("Card content")).toBeInTheDocument();
  });

  it("has glass-panel class", () => {
    const { container } = render(
      <AnimatedCard>
        <span>Content</span>
      </AnimatedCard>
    );

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass("glass-panel");
  });

  it("applies className prop", () => {
    const { container } = render(
      <AnimatedCard className="custom-class">
        <span>Content</span>
      </AnimatedCard>
    );

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass("custom-class");
    expect(wrapper).toHaveClass("glass-panel");
  });

  it("has transition-colors class by default", () => {
    const { container } = render(
      <AnimatedCard>
        <span>Content</span>
      </AnimatedCard>
    );

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass("transition-colors");
  });

  it("passes additional props to the wrapper div", () => {
    const { container } = render(
      <AnimatedCard data-testid="card">
        <span>Content</span>
      </AnimatedCard>
    );

    expect(screen.getByTestId("card")).toBeInTheDocument();
  });
});

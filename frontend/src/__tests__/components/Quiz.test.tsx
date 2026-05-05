import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QuizPanel } from "@/components/Quiz";
import type { Quiz } from "@/lib/api";


jest.mock("@/lib/sound", () => ({
  SoundManager: {
    click: jest.fn(),
    transition: jest.fn(),
    correct: jest.fn(),
    wrong: jest.fn(),
    achievement: jest.fn(),
    collect: jest.fn(),
    init: jest.fn(),
  },
}));

const MOCK_QUIZZES: Quiz[] = [
  {
    id: 1,
    question: "What is the closest planet to the Sun?",
    options: ["Mercury", "Venus", "Earth", "Mars"],
    difficulty: 1,
  },
  {
    id: 2,
    question: "What is the largest planet?",
    options: ["Jupiter", "Saturn", "Neptune", "Uranus"],
    difficulty: 2,
  },
];

describe("QuizPanel", () => {
  it("renders all quiz questions", () => {
    render(<QuizPanel quizzes={MOCK_QUIZZES} onComplete={jest.fn()} />);

    expect(screen.getByText("What is the closest planet to the Sun?")).toBeInTheDocument();
    expect(screen.getByText("What is the largest planet?")).toBeInTheDocument();
    expect(screen.getByText("Question 1")).toBeInTheDocument();
    expect(screen.getByText("Question 2")).toBeInTheDocument();
  });

  it("shows question text and options", () => {
    render(<QuizPanel quizzes={MOCK_QUIZZES} onComplete={jest.fn()} />);

    expect(screen.getByText("Mercury")).toBeInTheDocument();
    expect(screen.getByText("Venus")).toBeInTheDocument();
    expect(screen.getByText("Earth")).toBeInTheDocument();
    expect(screen.getByText("Mars")).toBeInTheDocument();
    expect(screen.getByText("Jupiter")).toBeInTheDocument();
    expect(screen.getByText("Saturn")).toBeInTheDocument();
  });

  it("allows selecting an answer", () => {
    render(<QuizPanel quizzes={MOCK_QUIZZES} onComplete={jest.fn()} />);

    const mercuryBtn = screen.getByText("Mercury");
    fireEvent.click(mercuryBtn);

    // After clicking, the button should have the selected styling class
    expect(mercuryBtn).toHaveClass("border-space-accent");
  });

  it("submit button is disabled until all questions are answered", () => {
    render(<QuizPanel quizzes={MOCK_QUIZZES} onComplete={jest.fn()} />);

    const submitBtn = screen.getByText("Submit Answers");
    expect(submitBtn).toBeDisabled();

    // Answer only the first question
    fireEvent.click(screen.getByText("Mercury"));
    expect(submitBtn).toBeDisabled();

    // Answer the second question
    fireEvent.click(screen.getByText("Jupiter"));
    expect(submitBtn).not.toBeDisabled();
  });

  it("calls onComplete with selected answers on submit", () => {
    const onComplete = jest.fn();
    render(<QuizPanel quizzes={MOCK_QUIZZES} onComplete={onComplete} />);

    fireEvent.click(screen.getByText("Mercury"));
    fireEvent.click(screen.getByText("Jupiter"));
    fireEvent.click(screen.getByText("Submit Answers"));

    expect(onComplete).toHaveBeenCalledWith([
      { quiz_id: 1, answer: "Mercury" },
      { quiz_id: 2, answer: "Jupiter" },
    ]);
  });

  it("shows disabled state after submission", () => {
    render(<QuizPanel quizzes={MOCK_QUIZZES} onComplete={jest.fn()} disabled />);

    const submitBtn = screen.getByText("Submitted");
    expect(submitBtn).toBeDisabled();

    // All option buttons should be disabled
    const optionButtons = screen.getAllByRole("button").filter((b) => b.textContent !== "Submitted");
    optionButtons.forEach((btn) => {
      expect(btn).toBeDisabled();
    });
  });
});

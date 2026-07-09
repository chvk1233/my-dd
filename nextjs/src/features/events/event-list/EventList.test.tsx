import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { fallbackEvents } from "@/entities/store-event";
import { EventDetail } from "@/features/events/event-detail/EventDetail";
import { EventList } from "./EventList";

describe("EventList", () => {
  it("renders event list items", () => {
    render(
      <EventList
        events={fallbackEvents}
        selectedEventId={fallbackEvents[0].event_id}
        onSelect={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "사건 목록" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /evt-001/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /evt-002/ })).toBeInTheDocument();
  });

  it("calls onSelect when an event is clicked", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();

    render(
      <EventList
        events={fallbackEvents}
        selectedEventId={fallbackEvents[0].event_id}
        onSelect={onSelect}
      />,
    );

    await user.click(screen.getByRole("button", { name: /evt-002/ }));
    expect(onSelect).toHaveBeenCalledWith("evt-002");
  });
});

describe("EventDetail", () => {
  it("shows selected event details", () => {
    render(<EventDetail event={fallbackEvents[1]} />);

    expect(screen.getByRole("heading", { name: "선택 사건" })).toBeInTheDocument();
    expect(screen.getByText("픽업 대기 시간 문의")).toBeInTheDocument();
    expect(screen.getByText("mobile_order")).toBeInTheDocument();
  });

  it("shows placeholder when event is missing", () => {
    render(<EventDetail />);
    expect(screen.getByText("선택된 사건의 상세 메시지를 확인합니다.")).toBeInTheDocument();
  });
});

export type Decision =
  | "act"
  | "no_action";

export type Priority =
  | "high"
  | "medium"
  | "low";

export type OfferType =
  | "none"
  | "reminder"
  | "discount"
  | "first_purchase";

export type ReviewStatus =
  | "pending"
  | "approved"
  | "edited"
  | "rejected";


export interface OfferRecommendation {
  cart_id: string;

  decision: Decision;

  priority: Priority;

  offer_type: OfferType;

  discount_percent: number | null;

  offer_description: string;

  reason: string;

  customer_message: string;

  risk_flags: string[];
}


export interface CartContext {
  fan_id: string;

  seats: number;

  section: string;

  cart_value: number;

  abandoned_hours: number;

  lifetime_tickets: number;

  days_since_last_purchase:
    | number
    | null;

  email_opt_in: boolean;
}


export interface RecommendationResponse {
  recommendation?: Partial<OfferRecommendation>;

  cart_context?: CartContext;
}


export interface ReviewItem
  extends OfferRecommendation {

  cart_context: CartContext;

  review_status: ReviewStatus;
}
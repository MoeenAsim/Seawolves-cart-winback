import type {
  CartContext,
  OfferRecommendation,
  RecommendationResponse,
  ReviewItem,
} from "@/types";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";


function normalizeRecommendation(
  item: RecommendationResponse
): ReviewItem {

  const recommendation =
    item.recommendation ?? {};

  const cartContext =
    item.cart_context ?? {
      fan_id: "",
      seats: 0,
      section: "",
      cart_value: 0,
      abandoned_hours: 0,
      lifetime_tickets: 0,
      days_since_last_purchase: null,
      email_opt_in: false,
    };


  const normalized:
    OfferRecommendation = {

    cart_id:
      recommendation.cart_id ?? "",

    decision:
      recommendation.decision ?? "no_action",

    priority:
      recommendation.priority ?? "low",

    offer_type:
      recommendation.offer_type ?? "none",

    discount_percent:
      recommendation.discount_percent ??
      null,

    offer_description:
      recommendation.offer_description ??
      "No win-back action recommended.",

    reason:
      recommendation.reason ??
      "No recommendation reason was provided.",

    customer_message:
      recommendation.customer_message ??
      "",

    risk_flags:
      Array.isArray(
        recommendation.risk_flags
      )
        ? recommendation.risk_flags
        : [],
  };


  return {
    ...normalized,

    cart_context:
      cartContext as CartContext,

    review_status: "pending",
  };
}


export async function getRecommendations():
  Promise<ReviewItem[]> {

  const response =
    await fetch(
      `${API_URL}/recommendations`,
      {
        method: "GET",
        cache: "no-store",
      }
    );


  if (!response.ok) {

    throw new Error(
      `Failed to load recommendations. ` +
      `Server returned ${response.status}.`
    );

  }


  const data =
    await response.json();


  if (!Array.isArray(data)) {

    throw new Error(
      "Invalid recommendation response."
    );

  }


  return data.map(
    (
      item: RecommendationResponse
    ) =>
      normalizeRecommendation(item)
  );
}
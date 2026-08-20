"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getRecommendations,
} from "@/lib/api";

import type {
  OfferRecommendation,
  ReviewItem,
  ReviewStatus,
} from "@/types";


export default function Home() {

  const [
    recommendations,
    setRecommendations,
  ] = useState<ReviewItem[]>([]);


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    error,
    setError,
  ] = useState<string | null>(null);


  const [
    filter,
    setFilter,
  ] = useState("all");


  const [
    editingId,
    setEditingId,
  ] = useState<string | null>(null);


  const [
    editMessage,
    setEditMessage,
  ] = useState("");


  const [
    editDiscount,
    setEditDiscount,
  ] = useState("");


  useEffect(() => {

    async function loadRecommendations() {

      try {

        setLoading(true);

        setError(null);


        const data =
          await getRecommendations();


        setRecommendations(data);


      } catch (err) {

        console.error(
          "Failed to load recommendations:",
          err
        );


        setError(
          "Unable to load cart recommendations."
        );


      } finally {

        setLoading(false);

      }

    }


    loadRecommendations();

  }, []);


  /* =========================================================
     STATS
  ========================================================= */

  const stats =
    useMemo(() => {

      const total =
        recommendations.length;


      const recommended =
        recommendations.filter(
          (item) =>
            item.decision === "act"
        ).length;


      const needsReview =
        recommendations.filter(
          (item) =>
            (item.risk_flags ?? []).length > 0
        ).length;


      const noAction =
        recommendations.filter(
          (item) =>
            item.decision === "no_action"
        ).length;


      return {
        total,
        recommended,
        needsReview,
        noAction,
      };

    }, [recommendations]);


  /* =========================================================
     FILTERS
  ========================================================= */

  const filteredRecommendations =
    useMemo(() => {

      if (filter === "all") {

        return recommendations;

      }


      if (filter === "recommended") {

        return recommendations.filter(
          (item) =>
            item.decision === "act"
        );

      }


      if (filter === "needs_review") {

        return recommendations.filter(
          (item) =>
            (item.risk_flags ?? []).length > 0
        );

      }


      if (filter === "no_action") {

        return recommendations.filter(
          (item) =>
            item.decision === "no_action"
        );

      }


      return recommendations;

    }, [
      recommendations,
      filter,
    ]);


  /* =========================================================
     UPDATE REVIEW STATUS
  ========================================================= */

  function updateStatus(
    cartId: string,
    status: ReviewStatus
  ) {

    setRecommendations(
      (current) =>
        current.map((item) =>
          item.cart_id === cartId
            ? {
                ...item,
                review_status: status,
              }
            : item
        )
    );

  }


  /* =========================================================
     START EDITING
  ========================================================= */

  function startEditing(
    recommendation: ReviewItem
  ) {

    setEditingId(
      recommendation.cart_id
    );


    setEditMessage(
      recommendation.customer_message
    );


    setEditDiscount(
      recommendation.discount_percent !==
        null
        ? recommendation.discount_percent.toString()
        : ""
    );

  }


  /* =========================================================
     SAVE EDIT
  ========================================================= */

  function saveEdit(
    cartId: string
  ) {

    setRecommendations(
      (current) =>
        current.map((item) => {

          if (
            item.cart_id !== cartId
          ) {

            return item;

          }


          let discount =
            item.discount_percent;


          if (
            editDiscount.trim() !== ""
          ) {

            const parsed =
              Number(editDiscount);


            if (
              Number.isFinite(parsed)
            ) {

              discount =
                Math.min(
                  15,
                  Math.max(
                    0,
                    parsed
                  )
                );

            }

          }


          return {
            ...item,

            customer_message:
              editMessage.trim(),

            discount_percent:
              discount,

            review_status:
              "edited",
          };

        })
    );


    setEditingId(null);

  }


  /* =========================================================
     LOADING STATE
  ========================================================= */

  if (loading) {

    return (

      <main className="loading-screen">

        <div className="loading-card">

          <div className="spinner" />

          <h2>
            Analyzing stale carts
          </h2>

          <p>
            The win-back agents are preparing
            recommendations.
          </p>

        </div>

      </main>

    );

  }


  /* =========================================================
     ERROR STATE
  ========================================================= */

  if (error) {

    return (

      <main className="loading-screen">

        <div className="error-card">

          <h2>
            Something went wrong
          </h2>

          <p>
            {error}
          </p>

          <button
            className="primary-button"
            onClick={() =>
              window.location.reload()
            }
          >
            Retry
          </button>

        </div>

      </main>

    );

  }


  /* =========================================================
     MAIN DASHBOARD
  ========================================================= */

  return (

    <main className="dashboard">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="topbar">

        <div>

          <div className="brand-row">

            <div className="team-mark">
              S
            </div>

            <div>

              <h1>
                Seattle Seawolves
              </h1>

              <p>
                Cart Win-Back
              </p>

            </div>

          </div>

        </div>


        <div className="agent-status">

          <span className="status-dot" />

          AI agents online

        </div>

      </header>


      {/* =====================================================
          INTRO
      ===================================================== */}

      <section className="intro">

        <div>

          <p className="eyebrow">
            MARKETER REVIEW
          </p>

          <h2>
            Cart win-back recommendations
          </h2>

          <p className="intro-text">
            Review AI-generated interventions
            before anything is sent to a fan.
          </p>

        </div>


        <div className="date-label">
          Last 7 days
        </div>

      </section>


      {/* =====================================================
          STATS
      ===================================================== */}

      <section className="stats-grid">

        <StatCard
          label="Stale carts"
          value={stats.total}
        />


        <StatCard
          label="Recommended"
          value={stats.recommended}
          accent
        />


        <StatCard
          label="Needs review"
          value={stats.needsReview}
          warning
        />


        <StatCard
          label="No action"
          value={stats.noAction}
        />

      </section>


      {/* =====================================================
          FILTERS
      ===================================================== */}

      <section className="toolbar">

        <div className="filter-group">

          <FilterButton
            label="All"
            active={
              filter === "all"
            }
            onClick={() =>
              setFilter("all")
            }
          />


          <FilterButton
            label="Recommended"
            active={
              filter === "recommended"
            }
            onClick={() =>
              setFilter("recommended")
            }
          />


          <FilterButton
            label="Needs review"
            active={
              filter === "needs_review"
            }
            onClick={() =>
              setFilter("needs_review")
            }
          />


          <FilterButton
            label="No action"
            active={
              filter === "no_action"
            }
            onClick={() =>
              setFilter("no_action")
            }
          />

        </div>


        <span className="result-count">

          {filteredRecommendations.length}{" "}

          {filteredRecommendations.length === 1
            ? "cart"
            : "carts"}

        </span>

      </section>


      {/* =====================================================
          RECOMMENDATIONS
      ===================================================== */}

      <section className="recommendations">

        {filteredRecommendations.map(
          (recommendation) => (

            <RecommendationCard
              key={
                recommendation.cart_id
              }

              recommendation={
                recommendation
              }

              editing={
                editingId ===
                recommendation.cart_id
              }

              editMessage={
                editMessage
              }

              editDiscount={
                editDiscount
              }

              onEditMessage={
                setEditMessage
              }

              onEditDiscount={
                setEditDiscount
              }

              onApprove={() =>
                updateStatus(
                  recommendation.cart_id,
                  "approved"
                )
              }

              onReject={() =>
                updateStatus(
                  recommendation.cart_id,
                  "rejected"
                )
              }

              onStartEdit={() =>
                startEditing(
                  recommendation
                )
              }

              onSaveEdit={() =>
                saveEdit(
                  recommendation.cart_id
                )
              }

              onCancelEdit={() =>
                setEditingId(null)
              }

            />

          )
        )}

      </section>


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer className="dashboard-footer">

        <span>
          AI recommendations require marketer
          approval before manual sending.
        </span>

        <span>
          No automated fan messaging is enabled.
        </span>

      </footer>

    </main>

  );

}


/* =========================================================
   STAT CARD
========================================================= */

function StatCard({
  label,
  value,
  accent = false,
  warning = false,
}: {
  label: string;
  value: number;
  accent?: boolean;
  warning?: boolean;
}) {

  return (

    <div className="stat-card">

      <span className="stat-label">
        {label}
      </span>


      <strong
        className={
          accent
            ? "stat-value accent"
            : warning
            ? "stat-value warning"
            : "stat-value"
        }
      >
        {value}
      </strong>

    </div>

  );

}


/* =========================================================
   FILTER BUTTON
========================================================= */

function FilterButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {

  return (

    <button
      type="button"

      className={
        active
          ? "filter-button active"
          : "filter-button"
      }

      onClick={onClick}
    >
      {label}
    </button>

  );

}


/* =========================================================
   RECOMMENDATION CARD
========================================================= */

function RecommendationCard({
  recommendation,
  editing,
  editMessage,
  editDiscount,
  onEditMessage,
  onEditDiscount,
  onApprove,
  onReject,
  onStartEdit,
  onSaveEdit,
  onCancelEdit,
}: {
  recommendation: ReviewItem;

  editing: boolean;

  editMessage: string;

  editDiscount: string;

  onEditMessage: (
    value: string
  ) => void;

  onEditDiscount: (
    value: string
  ) => void;

  onApprove: () => void;

  onReject: () => void;

  onStartEdit: () => void;

  onSaveEdit: () => void;

  onCancelEdit: () => void;
}) {

  const {
    cart_id,
    decision,
    priority,
    offer_type,
    discount_percent,
    offer_description,
    reason,
    customer_message,
    review_status,
  } = recommendation;


  /* =========================================================
     SAFE RISK FLAGS
  ========================================================= */

  const risk_flags =
    Array.isArray(
      recommendation.risk_flags
    )
      ? recommendation.risk_flags
      : [];


  const blocked =
    risk_flags.length > 0;


  /* =========================================================
     STATUS LABEL
  ========================================================= */

  const statusLabel =
    review_status === "approved"
      ? "Approved"
      : review_status === "edited"
      ? "Edited"
      : review_status === "rejected"
      ? "Rejected"
      : blocked
      ? "Needs review"
      : decision === "act"
      ? "Ready for review"
      : "No action";


  return (

    <article
      className={
        blocked
          ? "recommendation-card blocked"
          : "recommendation-card"
      }
    >

      {/* =====================================================
          CARD HEADER
      ===================================================== */}

      <div className="card-header">

        <div>

          <div className="cart-title-row">

            <span className="cart-id">
              {cart_id}
            </span>


            <StatusBadge
              priority={priority}
              status={statusLabel}
            />

          </div>


          <p className="card-subtitle">
            AI recommendation for marketer review
          </p>

        </div>


        <div className="review-status">
          {statusLabel}
        </div>

      </div>


      {/* =====================================================
          OFFER
      ===================================================== */}

      {decision === "act" ? (

        <div className="offer-section">

          <div className="offer-icon">

            {offer_type ===
            "first_purchase"
              ? "%"
              : offer_type ===
                "discount"
              ? "%"
              : "→"}

          </div>


          <div>

            <p className="offer-label">
              RECOMMENDED INTERVENTION
            </p>


            <h3>
              {offer_description}
            </h3>

          </div>

        </div>

      ) : (

        <div className="no-action-section">

          <span className="no-action-icon">
            —
          </span>


          <div>

            <p className="offer-label">
              RECOMMENDATION
            </p>


            <h3>
              No action
            </h3>

          </div>

        </div>

      )}


      {/* =====================================================
          REASON
      ===================================================== */}

      <div className="reason-section">

        <div className="section-heading">
          Why this recommendation?
        </div>


        <p>
          {reason}
        </p>

      </div>


      {/* =====================================================
          RISK FLAGS
      ===================================================== */}

      {blocked && (

        <div className="risk-section">

          <div className="risk-title">
            ⚠ Needs review before approval
          </div>


          {risk_flags.map(
            (flag) => (

              <div
                className="risk-flag"
                key={flag}
              >
                {flag}
              </div>

            )
          )}

        </div>

      )}


      {/* =====================================================
          CUSTOMER MESSAGE
      ===================================================== */}

      {decision === "act" && (

        <div className="message-section">

          <div className="section-heading">
            Customer message
          </div>


          {editing ? (

            <div className="edit-form">

              <label>
                Customer message
              </label>


              <textarea
                value={editMessage}

                onChange={(event) =>
                  onEditMessage(
                    event.target.value
                  )
                }

                rows={4}
              />


              {offer_type !==
                "reminder" &&
                offer_type !==
                  "none" && (

                <>

                  <label>
                    Discount %
                  </label>


                  <input
                    type="number"

                    min="0"

                    max="15"

                    step="0.5"

                    value={
                      editDiscount
                    }

                    onChange={(event) =>
                      onEditDiscount(
                        event.target.value
                      )
                    }
                  />

                </>

              )}


              <div className="edit-actions">

                <button
                  type="button"
                  className="primary-button"

                  onClick={
                    onSaveEdit
                  }
                >
                  Save changes
                </button>


                <button
                  type="button"
                  className="secondary-button"

                  onClick={
                    onCancelEdit
                  }
                >
                  Cancel
                </button>

              </div>

            </div>

          ) : (

            <div className="customer-message">

              {customer_message || (
                <span>
                  No customer message provided.
                </span>
              )}

            </div>

          )}

        </div>

      )}


      {/* =====================================================
          ACTIONS
      ===================================================== */}

      {decision === "act" && (

        <div className="card-actions">

          {!editing && (

            <>

              <button
                type="button"

                className={
                  blocked
                    ? "primary-button disabled-button"
                    : "primary-button"
                }

                disabled={
                  blocked ||
                  review_status ===
                    "approved"
                }

                onClick={
                  onApprove
                }
              >
                ✓ Approve
              </button>


              <button
                type="button"
                className="secondary-button"

                onClick={
                  onStartEdit
                }
              >
                ✎ Edit
              </button>


              <button
                type="button"
                className="danger-button"

                onClick={
                  onReject
                }
              >
                Reject
              </button>

            </>

          )}

        </div>

      )}

    </article>

  );

}


/* =========================================================
   STATUS BADGE
========================================================= */

function StatusBadge({
  priority,
  status,
}: {
  priority: string;
  status: string;
}) {

  return (

    <span
      className={`status-badge ${priority}`}
    >
      {status}
    </span>

  );

}
(* RH-Omega: an elementary logical warning, not a proof of RH.
   This finite-prefix countermodel is an arbitrary integer sequence,
   not the Li coefficients of the actual Riemann zeta function. *)
From Coq Require Import ZArith Lia.
Open Scope Z_scope.

Definition prefix_countermodel (cutoff n : nat) : Z :=
  if Nat.leb n cutoff then 1 else -1.

Theorem prefix_positive :
  forall (cutoff n : nat),
    (n <= cutoff)%nat -> 0 <= prefix_countermodel cutoff n.
Proof.
  intros cutoff n H.
  unfold prefix_countermodel.
  assert (Hleb : Nat.leb n cutoff = true) by (apply Nat.leb_le; exact H).
  rewrite Hleb.
  lia.
Qed.

Theorem finite_prefix_not_universal :
  forall cutoff : nat,
    ~ (forall n : nat, 0 <= prefix_countermodel cutoff n).
Proof.
  intros cutoff H.
  specialize (H (S cutoff)).
  unfold prefix_countermodel in H.
  assert (Hleb : Nat.leb (S cutoff) cutoff = false)
    by (apply Nat.leb_gt; lia).
  rewrite Hleb in H.
  lia.
Qed.

Print Assumptions prefix_positive.
Print Assumptions finite_prefix_not_universal.

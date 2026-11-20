(* Millennium Ω TECT policy model in Coq.
   Only local acceptance logic is checked, NOT any Millennium conjecture. *)

Inductive evidence_scope : Type :=
| bounded
| global.

Definition accept (s : evidence_scope) (independently_reviewed : bool) : bool :=
  match s with
  | bounded => false
  | global => independently_reviewed
  end.

Theorem bounded_rejected :
  forall (review : bool), accept bounded review = false.
Proof.
  intro review.
  reflexivity.
Qed.

Theorem unreviewed_rejected :
  forall (s : evidence_scope), accept s false = false.
Proof.
  intro s.
  destruct s; reflexivity.
Qed.

Print Assumptions bounded_rejected.
Print Assumptions unreviewed_rejected.

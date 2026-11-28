import F038Formal.Resources

namespace MathOS.F038.Resources.Tests
open MathOS.F038.Resources

-- Counts from the executed D7I 189-coordinate projection fixture.
def php6 : Counts := ⟨84,504,3486,252,126,13,13⟩

theorem php6_valid : ValidCounts 378 504 php6 :=
  countsCheck_sound (by decide)

example : countsCheck 378 504 php6 = true := by decide
example : countsCheck 378 504 {php6 with starts := 379} = false := by decide
example : countsCheck 378 504 {php6 with peakQueue := 379} = false := by decide
example : work php6 = 4242 := by decide
example : bound 378 504 = 54343548 := by decide
example : payloadWords 28 126 252 = 1164 := by decide
example : payloadBits 18 28 126 252 = 20952 := by decide
example : charge 4242 4241 = some 4242 := by decide
example : charge 4242 4242 = none := by decide
example : charge 0 0 = none := by decide
example : checkerBound 42 252 = 444528 := by decide

theorem fixture_work_safe : work php6 ≤ bound 378 504 :=
  charged_work_bound php6_valid

theorem fixture_payload_safe :
    payloadBits 18 28 126 252 ≤ 18 * (2 + 280 + 3*(378*378) + 3*(378*378*378)) :=
  payload_bit_bound (f := 280) php6_valid (by decide) (by decide)

theorem fixture_live_safe :
    liveWords 378 504 28 252 php6 ≤
      3*504 + 9*378 + 1 + (2+280+3*(378*378)+3*(378*378*378)) :=
  live_word_bound (f := 280) php6_valid (by decide) (by decide)

#print axioms fixture_work_safe
#print axioms fixture_payload_safe
#print axioms fixture_live_safe

end MathOS.F038.Resources.Tests

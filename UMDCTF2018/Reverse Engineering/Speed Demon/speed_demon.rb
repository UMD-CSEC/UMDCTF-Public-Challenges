#!/usr/bin/env/ruby

require "fiddle"

@v = ?l
X1 = %@#{%$#{?:*2}$+%&&+%_F_+("%<qq>s"%{qq: ?i})+%%#{?d*2}%}#@v@+?e
X2 = %@#{?H}a%<ldn>s#{X1[-1]}@%{ldn: :ndl}
X3 = %^#{X1[-6]}#{?u}#{X2[2]}^+?c+?t+%(#{X1[3]}%<no>s)%{no: :on}

LFDY = "\u0004\b[\u0013\"-YARVInstructionSequence/SimpleDataFormati\ai\ni\u0006{\t:\rarg_sizei\u0000:\u000Flocal_sizei\u0016:\u000Estack_maxi\a:\u000Fcode_range[\ti\u0006i\u0000i\"i\bI\"\u000F<compiled>\u0006:\u0006EF@\t0i\u0006:\btop[\u0016:\aq1:\aqx:\aq2:\aq3:\aq4:\aq5:\aq6:\aq7:\aq8:\aq9:\bq10:\bq11:\bq12:\bq13:\bq14:\bq15:\aqy{\u0000[\u0000[vi\u0006:\u0014RUBY_EVENT_LINE[\a:\u000EputstringI\"\u0006U\u0006;\tT[\a:\u0015putspecialobjecti\b[\a:\u0010setconstant:\u0006Ui\a;\u001C[\a;\u001DI\"\u0006M\u0006;\tT[\a;\u001Ei\b[\a;\u001F:\u0006Mi\b;\u001C[\a;\u001DI\"\u0006D\u0006;\tT[\a;\u001Ei\b[\a;\u001F:\u0006Di\t;\u001C[\a;\u001DI\"\u0006C\u0006;\tT[\a;\u001Ei\b[\a;\u001F:\u0006Ci\n;\u001C[\a;\u001DI\"\u0006T\u0006;\tT[\a;\u001Ei\b[\a;\u001F:\u0006Ti\v;\u001C[\a;\u001DI\"\u0006F\u0006;\tT[\a;\u001Ei\b[\a;\u001F:\u0006Fi\f;\u001C[\a;\u001DI\"\u0006-\u0006;\tT[\a:\u0017setlocal_OP__WC__0i\u0018i\r;\u001C[\a;\u001DI\"\u0006{\u0006;\tT[\a;&i\u0017i\u000E;\u001C[\a;\u001DI\"\u0006N\u0006;\tT[\a;&i\u0016i\u000F;\u001C[\a;\u001DI\"\u0006E\u0006;\tT[\a;&i\u0015i\u0010;\u001C[\a;\u001DI\"\u0006S\u0006;\tT[\a;&i\u0014i\u0011;\u001C[\b:\u0013getinlinecache:\rlabel_63i\u0000[\a:\u0010getconstant;$[\a:\u0013setinlinecachei\u0000;([\a;&i\u0013i\u0012;\u001C[\a:\u0017getlocal_OP__WC__0i\u0015[\a;&i\u0012i\u0013;\u001C[\b;':\rlabel_76i\u0006[\a;);\"[\a;*i\u0006;,[\a;&i\u0011i\u0014;\u001C[\a;\u001DI\"\u0006B\u0006;\tT[\a;&i\u0010i\u0015;\u001C[\a;\u001DI\"\u0006Y\u0006;\tT[\a;&i\u000Fi\u0016;\u001C[\a;+i\u0013[\a;&i\u000Ei\u0017;\u001C[\a;+i\u0012[\a;&i\ri\u0018;\u001C[\b;':\u000Elabel_101i\a[\a;);#[\a;*i\a;-[\a;&i\fi\u0019;\u001C[\a;\u001DI\"\u0006O\u0006;\tT[\a;&i\vi\u001A;\u001C[\a;+i\u0011[\a;&i\ni\e;\u001C[\a;+i\r[\a;&i\ti\u001C;\u001C[\a;\u001DI\"\u0006}\u0006;\tT[\a;&i\bi!;\u001C[\u0006:\fputself[\a;\u001DI\"\"NTS: Deoptimize prints later.\u0006;\tT[\b:\eopt_send_without_block{\b:\bmid:\tputs:\tflagi-:\u000Eorig_argci\u0006F[\u0006:\nleave"

class Object
  def _c(s)
    method(:class_eval).to_proc.call s
  end
end

def nm
  {}
end

module V
  module_function

  def e(s)
    h = (_c X1)
      ._c(X2)
      ._c("#{X2[3].method(:upcase).call}#{X2[-1].method(:upcase).call}#{X1[-6]}AULT")["rb_#{X1[3]}s#{X2[-1]}q_load"]
    (_c X1)
      ._c(X3)
      .new(h, [(_c X1)
        ._c("#{X3[4].method(:upcase).call}YP#{X2[-1].method(:upcase).call}_VOIDP")] * 3, (_c X1)
        ._c("#{X3[4].method(:upcase).call}YP#{X2[-1].method(:upcase).call}_VOIDP"))
      .call((_c X1).dlwrap(s), nm[%%%], nm[%_x_]).to_value.method(:eval).to_proc.call
  end
end

V.method(?e.to_sym).call (Marshal).method(:load).method(:call).call LFDY

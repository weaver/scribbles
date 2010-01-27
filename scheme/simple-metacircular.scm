;;;; A simple meta-circular evaluator.

;;;; An example session is:
;;;;
;;;;    > (repl *primitive*)
;;;;    Welcome to the meta-circular REPL (^D to quit).
;;;;    repl> (define (inc a) (+ a 1))
;;;;    repl> (inc 2)
;;;;    3
;;;;    repl> ^D
;;;;    Leaving the meta-circular REPL.
;;;;    >


;;; REPL

(define (repl env)
  (display "\nWelcome to the meta-circular REPL (^D to quit).\n")
  (repl-loop (prompt) env))

(define (repl-loop form env)
  (if (eof-object? form)
      (display "\nLeaving the meta-circular REPL.\n")
      (receive (value env) (meta-eval form env)
        (if (not (undefined? value))
            (begin
              (display value)
              (newline)))
        (repl-loop (prompt) env))))

(define (prompt)
  (display "repl> ")
  (read))


;;; Evaluation

(define (meta-eval form env)
  (cond ((atom? form)
         (values form env))
        ((name? form)
         (values (lookup form env) env))
        ((eq? (car form) 'define)
         (values *undefined* (add-definition form env)))
        ((eq? (car form) 'cond)
         (eval-cond (cdr form) env))
        (else
         (eval-apply
          (eval->value (car form) env)
          (eval-list (cdr form) env)
          env))))

(define (eval->value form env)
  (receive (value _) (meta-eval form env)
    value))

(define (eval-apply operator operands env)
  (cond ((primitive? operator)
         (values (primitive-apply operator operands) env))
        ((meta-procedure? operator)
         (receive (params body) (unstructure-procedure operator)
           (values (eval->value body (add-frame params operands env))
                   env)))
        (else
         (error 'bad-operator operator))))

(define (eval-list forms env)
  (map (lambda (form)
         (eval->value form env))
       forms))

(define (eval-cond forms env)
  (cond ((null? forms)
         (values *undefined* env))
        ((or (eq? (caar forms) 'else)
             (eval->value (caar forms) env))
         (values (eval->value (cadar forms) env) env))
        (else
         (eval-cond (cdr forms) env))))


;;; Definitions

(define (unstructure-define form)
  (values (def-name form)
          (def-params form)
          (def-body form)))

(define def-name caadr)
(define def-params cdadr)
(define def-body caddr)


;;; Procedures

(define (meta-procedure params body)
  (list params body))

(define meta-procedure? pair?)

(define (unstructure-procedure proc)
  (values (proc-params proc)
          (proc-body proc)))

(define proc-params car)
(define proc-body cadr)


;;; Environments

(define name? symbol?)

(define (add-definition form env)
  (receive (name params body) (unstructure-define form)
    (add-binding name (meta-procedure params body) env)))

(define (add-binding name value env)
  (cons (bind name value)
        env))

(define (add-frame names values env)
  (if (!= (length names) (length values))
      (error 'name-value-mismatch names values)
      (append (map bind names values) env)))

(define bind list)

(define (lookup name env)
  (cond ((assq name env) => cadr)
        (else (error '|lookup: undefined| name))))


;;; Misc

(define (atom? value)
  (or (string? value)
      (number? value)
      (boolean? value)
      (null? value)))

(define *undefined* '&undefined)

(define (undefined? value)
  (eq? value *undefined*))

(define (!= . values)
  (not (apply = values)))


;;; Primitives

(define primitive? procedure?)
(define primitive-apply apply)

(define *primitive*
  `((cons ,cons)
    (list ,list)
    (null? ,null?)
    (pair? ,pair?)
    (car ,car)
    (cdr ,cdr)
    (number? ,number?)
    (string? ,string)
    (boolean? ,boolean?)
    (+ ,+)
    (- ,-)
    (* ,*)
    (/ ,/)
    (= ,=)
    (> ,>)
    (< ,<)
    (eq? ,eq?)))

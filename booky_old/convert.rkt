;;; Convert s-expression publication struct to toml format.
;;; Use raco to install the toml package; it's not part of Racket.
;;;
;;; $ raco pkg install toml
;;;

#lang racket

(require toml)

(define publication-in-filename (make-parameter "publication.rkt"))
(define publication-out-filename (make-parameter "publication.toml"))
(struct publication (schema rows) #:prefab)
(define (read-publications) (call-with-input-file (publication-in-filename) read))

;; Read in the publications database and construct 
;; a plain alist from each publication data.
;; Alist items are in the form (schema-heading . value)

(define (publications->alists)
 (let ((mydata (read-publications)))
   (map (lambda (row)
          (map (lambda (head item)
                 (cons (second head) item))
               (publication-schema mydata)
               (vector->list row)))
        (publication-rows mydata))))

;; Publications are now in a list of alists.
;; We want to extract the "code" and use that 
;; as a hasheq key. The value for this key
;; is another hasheq initialised with the rest 
;; of the alist pairs (with the code pair removed.

(define (build-publications-hasheq)
 (let ((big-ht (make-hasheq)))
   (for-each 
    (lambda (alist)
     (let ((code-pair (assoc 'code alist)))
         (hash-set! big-ht 
                    (string->symbol (cdr code-pair))
                    (let ((ht (make-hasheq)))
                             (for-each (lambda (u)
                                        (hash-set! ht (car u) (cdr u)))
                                        (remq code-pair alist))
                             ht))))
               (publications->alists))
   big-ht))

;; Write the big-ht hash table to file.
;; Luckily racket's toml writer seems to always
;; do it in alphabetical order.

(define out (open-output-file (publication-out-filename) #:exists 'truncate))
(display (tomlexpr->string
          (build-publications-hasheq))
          out)
(close-output-port out)


